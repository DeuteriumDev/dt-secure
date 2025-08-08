import fs from "fs";
import yaml from "yaml";
import process from "process";
import path from "path";

import { DtConfig } from "../types";

const CONFIG_FILE = ".dt-ac.yml";
class DtConfigError extends Error {}

/**
 * Finds the nearest DT-CONFIG file by searching upward from the current working directory.
 * @returns The absolute path to the config file, or null if not found
 */
export function findConfig(): string {
  let dir = process.cwd();
  while (true) {
    const pkgPath = path.join(dir, CONFIG_FILE);
    if (fs.existsSync(pkgPath)) {
      return pkgPath;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new DtConfigError("Config file not found in current tree");
}

/**
 * Reads and parses a YAML file from the given path.
 * @param {string} configPath
 * @returns Parsed DT-Config content as an object
 * @throws {DtConfigError}
 */
export function readConfigFile(configPath: string): DtConfig {
  const fileContent = fs.readFileSync(configPath, "utf8");
  return yaml.parse(fileContent);
}

const configPath = findConfig();
const config = readConfigFile(configPath);

export { config };
