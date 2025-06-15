import {
  addRemote,
  getConfig,
  secureTable,
  fetchRemoteConfig,
} from "../main.mjs";

describe("main.mjs", () => {
  describe("addRemote", () => {
    it("should run without sql errors", async () => {
      await addRemote();
    });
  });

  describe("fetchRemoteConfig", () => {
    it("should run without errors", async () => {
      const results = fetchRemoteConfig(
        () => ({
          json: () => Promise.resolve({ test: 1 }),
        }),
        "test-url",
        "test-apiKey"
      );
      expect(results).toEqual({ test: 1 });
    });
  });
});
