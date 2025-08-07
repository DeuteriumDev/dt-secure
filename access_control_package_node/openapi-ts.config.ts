import { defineConfig, defaultPlugins } from "@hey-api/openapi-ts";

export default defineConfig({
  // @ts-ignore
  client: "@hey-api/client-fetch",
  input: "../access_manager_api/schema.yml",
  output: "./src/codegen/",
  plugins: [
    ...defaultPlugins,
    {
      enums: false,
      name: "@hey-api/typescript",
    },
    "zod",
  ],
});
