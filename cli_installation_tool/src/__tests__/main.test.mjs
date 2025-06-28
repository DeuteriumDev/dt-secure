import { PGlite } from "@electric-sql/pglite";
import {
  vi,
  describe,
  it,
  expect,
  beforeAll,
  beforeEach,
  afterEach,
  afterAll,
} from "vitest";
import pg from "pg";

import {
  addRemote,
  getConfig,
  secureTable,
  fetchRemoteConfig,
} from "../main.mjs";

describe("main.mjs", () => {
  describe("addRemote", () => {
    let client;
    beforeAll(async () => {
      client = new pg.Client({
        connectionString: process.env.PG_URL,
      });
      await client.connect();
    });

    afterAll(async () => {
      await client.end();
    });

    it("should run without sql errors", async () => {
      await addRemote(client, {
        dt_schema: "test",
        pg_url: process.env.PG_URL,
        is_local: true,
        security_table_name: "test_security",
      });
    });
  });

  describe("fetchRemoteConfig", () => {
    it("should run without errors", async () => {
      const results = await fetchRemoteConfig(
        () => ({
          ok: true,
          json: () => Promise.resolve({ test: 1, ok: true }),
        }),
        "test-url",
        "test-apiKey"
      );
      expect(results).toEqual({ test: 1, ok: true });
    });
  });
});
