import fs from "node:fs/promises";
import yargs from "yargs";
import yaml from "yaml";
import pg from "pg";

const CONFIGS = {
  table: "dt_table",
  server: "dt_server",
  readPolicy: "dt_policy_read",
  getUser: "getCurrentUser",
};

Object.freeze(CONFIGS);

/**
 * Get DT config from local file
 * @param {string} file - name of config file to try and read from
 * @returns
 */
export async function getConfig(file) {
  await fs.access(configFile, fs.constants.R_OK);
  const fileContent = await fs.readFile(file, { encoding: "utf-8" });
  const config = yaml.parse(fileContent);
  const resolvedFile = JSON.stringify(config).replace(
    /\$\{(\w+)\}/g,
    (_, envVar) => {
      return process.env[envVar];
    }
  );
  return JSON.parse(resolvedFile);
}

/**
 * @typedef {Oject} DtConfig
 * @property {string} dt_api_key - api key from config file
 * @property {string} dt_url - api key from config file
 */

/**
 * Get server config from provided url
 * @param {fetch} fetchClient - a function that either is, or emulates [fetch] api
 * @param {DtConfig} dt_config - configuration file type
 * @returns {Object}
 */
export async function fetchRemoteConfig(fetchClient, dt_config) {
  const response = await fetchClient(dt_config.dt_url, {
    method: "post",
    headers: {
      "api-key": dt_config.dt_api_key,
    },
    body: dt_config,
  });
  if (!response.ok) {
    throw new Error(
      `Failed to fetch remote config: ${response.status} ${response.statusText}`
    );
  }
  const data = await response.json();
  return data;
}

export async function addRemote(
  client,
  { url, database, port, user, password, dt_schema: schema }
) {
  await client.query(`
    CREATE EXTENSION IF NOT EXISTS postgres_fdw;

    DROP SERVER IF EXISTS "${schema}.${CONFIGS.server}" CASCADE;
    
    CREATE SERVER "${schema}.${CONFIGS.server}"
      FOREIGN DATA WRAPPER postgres_fdw
      OPTIONS (host '${url}', dbname '${database}', port '${port}');

    CREATE USER MAPPING FOR CURRENT_USER
      SERVER "${schema}.${CONFIGS.server}"
      OPTIONS (user '${user}', password '${password}');

    CREATE FOREIGN TABLE "${schema}.${CONFIGS.table}" (
        user_id varchar(40) NOT NULL,
        resource_id varchar(40) NOT NULL,
        can_create boolean NOT NULL,
        can_read boolean NOT NULL,
        can_update boolean NOT NULL,
        can_delete boolean NOT NULL
      )
      SERVER "${schema}.${CONFIGS.server}";
  `);
}

export async function secureTable(client, { schema }, tableName) {
  await client.query(`
    ALTER TABLE "${schema}.${tableName}" ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "${schema}.${CONFIGS.readPolicy}_${tableName}"
      ON "${schema}.${tableName}"
      FOR SELECT
      USING (
        ID IN (
          SELECT user_id
          FROM "${schema}.${CONFIGS.table}"
          WHERE can_read = true AND user_id = ${schema}.${CONFIGS.getUser}()
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
  const client = new pg.Client({
    connectionString: localConfig.pg_url,
  });
  await client.connect();

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
  .help().argv;

main(argv).catch((err) => {
  console.error(err);
  process.exit(1);
});
