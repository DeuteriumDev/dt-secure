import fs from "node:fs/promises";
import yargs from "yargs";
import yaml from "yaml";
import pg, { Client } from "pg";
import { parse } from "pg-connection-string";
import _ from "lodash";
import { config } from "dotenv";

import CONFIGS from "./configs.json";

import "./types/types.js";

Object.freeze(CONFIGS);

/**
 * Get DT config from local file
 * @param {string} file - name of config file to try and read from
 * @returns
 */
export async function getConfig(file) {
  let config;
  if (file.startsWith("string:")) {
    config = JSON.parse(file.replace("string:", ""));
  } else {
    await fs.access(file, fs.constants.R_OK);
    const fileContent = await fs.readFile(file, { encoding: "utf-8" });
    config = yaml.parse(fileContent);
  }
  const resolvedFile = JSON.stringify(config).replace(
    /\$\{(\w+)\}/g,
    (_, envVar) => {
      return process.env[envVar];
    }
  );
  return JSON.parse(resolvedFile);
}

/**
 * Get server config from provided url
 * @param {fetch} fetchClient - a function that either is, or emulates [fetch] api
 * @param {DtConfig} dt_config - configuration file type
 * @returns {Object}
 */
export async function fetchRemoteConfig(fetchClient, dt_config) {
  const response = await fetchClient(dt_config.dt_url || CONFIGS.dt_url, {
    method: "get",
    headers: {
      Authorization: `Token ${dt_config.dt_api_key}`,
    },
  });
  if (!response.ok) {
    throw new Error(
      `Failed to fetch remote config: ${response.status} ${response.statusText}`
    );
  }
  const data = await response.json();
  const remoteConfig = _.get(data, "results[0]", null);
  if (!remoteConfig) throw new Error("Invalid remote config");
  return remoteConfig;
}

/**
 *
 * @param {Client} client - pg client instance
 * @param {DtConfig} dt_config - config file data
 */
export async function addRemote(
  client,
  { pg_url, dt_schema: schema, security_table_name }
) {
  const pgConfig = parse(pg_url);

  // add [schema] if provided and it's not the public schema
  if (schema !== "public") {
    await client.query(`
      CREATE SCHEMA IF NOT EXISTS "${schema}";
    `);
  }

  // use default postgres port when running locally because the server will
  // be "internal" to docker ie default ports
  const isLocal = /(localhost)|(127\.0\.0\.1)|(0\.0\.0\.0)/.test(pg_url);
  const port = isLocal ? "5432" : pgConfig.port;
  // install the server
  await client.query(`
    CREATE EXTENSION IF NOT EXISTS postgres_fdw;
  `);
  await client.query(`
    DROP SERVER IF EXISTS "${CONFIGS.server}" CASCADE;
  `);
  await client.query(`
    CREATE SERVER "${CONFIGS.server}"
      FOREIGN DATA WRAPPER postgres_fdw
      OPTIONS (host '${pgConfig.host}', dbname '${pgConfig.database}', port '${port}');
  `);
  await client.query(`
    CREATE USER MAPPING FOR CURRENT_USER
      SERVER "${CONFIGS.server}"
      OPTIONS (user '${pgConfig.user}', password '${pgConfig.password}');
  `);

  // make a circular table to test the connection with
  if (isLocal) {
    // test server integration
    const testTableName = `demo-${String(Math.random()).slice(-4, -1)}`;
    const targetSchema = pgConfig.schema || "public";
    await client.query(`
        CREATE TABLE "${targetSchema}"."${testTableName}" (
          id uuid primary key
        );
    `);
    await client.query(`
        INSERT INTO "${targetSchema}"."${testTableName}" VALUES (gen_random_uuid());
    `);

    await client.query(`
        IMPORT FOREIGN SCHEMA "${targetSchema}" LIMIT TO ("${targetSchema}"."${testTableName}") FROM SERVER "${CONFIGS.server}" INTO "${schema}";
    `);

    const results = await client.query(
      `select count(*) as count from "${schema}"."${testTableName}"`
    );
    await client.query(`
      DROP TABLE "${targetSchema}"."${testTableName}" CASCADE;
    `);
    if (results.rows[0].count === 0) {
      throw new Error("PGServerError: fdw server installation failed");
    }
  } else {
    await client.query(`
      IMPORT FOREIGN SCHEMA "${security_table_name.split(
        "."[0]
      )}" LIMIT TO ("${security_table_name
        .split(".")
        .join('"."')}") FROM SERVER "${schema}.${
        CONFIGS.server
      }" INTO "${schema}";
    `);

    const results = await client.query(
      `select count(*) from "${security_table_name} limit 1"`
    );
    if (results.rows[0].count === 0) {
      throw new Error("PGServerError: fdw server installation failed");
    }
  }
}

/**
 * Decorate given [tableName] with dt policy
 *
 * @param {Client} client - sql client
 * @param {DtConfig} dt_config - config object
 * @param {string} tableName - target table name
 */
export async function secureTable(
  client,
  { dt_schema, security_table_name },
  tableName
) {
  await client.query(`
    ALTER TABLE "${tableName}" ENABLE ROW LEVEL SECURITY;
  `);
  await client.query(`
    CREATE POLICY "${dt_schema}.${CONFIGS.readPolicy}_${tableName}"
      ON "${tableName}"
      FOR SELECT
      USING (
        EXISTS (
          SELECT 1
          FROM "${dt_schema}.${security_table_name}"
          WHERE
            ${dt_schema}.${CONFIGS.getUser}() IS null OR (
              "${CONFIGS.canReadColumName}" = true
              AND user_id = ${schema}.${CONFIGS.getUser}()
              AND "${CONFIGS.resourceColumnName}" = ID
            )
        )
      );
  `);
}

/**
 * @param {{config: string}} configFile - path to config file
 */
async function main({ config }) {
  const configFile = process.env.DT_CONFIG || config;
  const localConfig = await getConfig(configFile);
  const remoteConfig = fetchRemoteConfig(fetch, localConfig);
  let client;

  // build proxy object to log all outputs
  if (process.env.DEBUG) {
    client = {
      _client: new pg.Client({
        connectionString: localConfig.pg_url,
      }),
      query: async (...args) => {
        const results = await client._client.query(...args);
        console.log([...args, JSON.stringify(results, null, 2)]);
        return results;
      },
      end: async () => await client._client.end(),
      connect: async () => await client._client.connect(),
    };
  } else {
    client = new pg.Client({
      connectionString: localConfig.pg_url,
    });
  }
  client = await client.connect();

  await addRemote(client, { ...remoteConfig, ...localConfig });
  await Promise.all(
    localConfig.tables.map((t) => {
      secureTable(client, t);
    })
  );
}

const argv = yargs(process.argv.slice(2))
  .option("config", {
    type: "string",
    description: "Path to config file, defaults to '.dt-ac.yml'",
    default: ".dt-ac.yml",
  })
  .option("env", {
    type: "string",
    description: "Path to env file, defaults to '.env'",
    default: ".env",
  })
  .help().argv;

config({ path: argv.env });
if (require.main === module) {
  main(argv).catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
