
import fs from "fs";
import yaml from "yaml";

/**
 * Reads and parses a YAML file from the given path.
 * @param filePath Path to the YAML file
 * @returns Parsed DT-COnfig content as an object
 */
export function readConfigFile(filePath: string) {
  const fileContent = fs.readFileSync(filePath, "utf8");
  return yaml.parse(fileContent);
}
