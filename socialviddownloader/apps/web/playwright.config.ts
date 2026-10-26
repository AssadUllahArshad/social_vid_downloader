import { defineConfig, devices } from "@playwright/test";
const baseURL=process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";
export default defineConfig({
  testDir: "./e2e",
  use: { baseURL },
  // Release verification must reach the explicitly started standalone build.
  // Do not silently reuse or start a development server for that run.
  webServer: process.env.PLAYWRIGHT_EXTERNAL_SERVER === "1" ? undefined : {
    command: process.env.CI ? "npm run start -- --hostname 127.0.0.1 --port 3000" : "npm run dev",
    url: baseURL,
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
});
