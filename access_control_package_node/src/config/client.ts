import type { CreateClientConfig } from "../codegen/client.gen";
import { config as cliConfig } from "./cli";

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  baseUrl: cliConfig.dt_url,
  auth: () => `Token ${cliConfig.dt_api_key}`,
});
