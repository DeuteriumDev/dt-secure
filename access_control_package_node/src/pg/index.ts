import { Client, ClientBase, QueryResult } from "pg";

/**
 * @callback QueryCallback
 * @param {ClientBase} args
 */

/**
 * Wraps a pg Client instance and sets the user for a given query or for the duration of the client.
 * @param {Client} client - The pg Client instance
 * @param {string} user - the user to authorize the session with
 * @param {QueryCallback} [callback] - The query function to execute after setting the user
 */
async function withAC<T>(client: Client, user: string): Promise<Client>;
async function withAC<T>(
  client: Client,
  user: string,
  callback?: (qx: Client) => Promise<T>
): Promise<T>;
async function withAC<T>(
  client: Client,
  user: string,
  callback?: (qx: Client) => Promise<T>
): Promise<T | Client> {
  await client.query(`set local "dt.user" = '${user}';`);

  if (callback) {
    const results = await callback(client);
    await client.query(`reset "dt.user";`);
    return results;
  }
  return client;
}

/**
 * Example function to confirm the DX of the helper
 */
async function doStuff() {
  const client = new Client();
  const results = await withAC(client, "test", (cx) =>
    cx.query("select * from table")
  );
  console.log(results);

  const secureClient = await withAC(client, "test2");
  const otherResults = await secureClient.query("test");
  console.log(otherResults);
}

export { withAC };
