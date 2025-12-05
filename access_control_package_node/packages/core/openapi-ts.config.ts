import { defineConfig, defaultPlugins } from "@hey-api/openapi-ts";

export default defineConfig({
  // @ts-ignore
  client: "@hey-api/client-fetch",
  input: "../access_manager_api/schema.yml",
  output: "./src/codegen/",
  plugins: [
    {
      enums: false,
      name: "@hey-api/typescript",
    },
    {
      name: "@hey-api/client-fetch",
      runtimeConfigPath: "./src/config/client.ts", // interface w/ dt config here
    },
    {
      name: "@hey-api/sdk",
      auth: false,
    },
  ],
});
