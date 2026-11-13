import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globalSetup: ["./test/server.ts"],
    include: ["test/**/*.test.ts"],
    testTimeout: 15_000,
  },
});
