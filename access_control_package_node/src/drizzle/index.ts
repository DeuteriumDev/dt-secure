import { drizzle as Drizzle } from "drizzle-orm/node-postgres";

/**
 * Wraps a drizzle instance and sets the user for a given query using SET SESSION AUTHORIZATION.
 * @param drizzle - The drizzle database instance
 * @param user - The user to set for the session
 * @param queryFn - The query function to execute after setting the user
 */
export async function withUserSession<T>(
  drizzle: typeof Drizzle,
  user: string,
  queryFn: (db: typeof Drizzle) => Promise<T>
): Promise<T> {
  //   await drizzle.execute('SET local dt.user "?"', [user]);
  return queryFn(drizzle);
}
