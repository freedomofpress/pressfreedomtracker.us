import { readFile } from "fs/promises";

import { test, expect, type Page } from "@playwright/test";

// Incident export tests, originating with our QA checklist item:
//
//  "Verify Incident Export works"
//
// These export a single category, taken from the home page's category links,
// to keep the export size managable.

const INCIDENTS = "/all-incidents/";

// The title of the first category linked from the home page
async function firstCategory(page: Page): Promise<string> {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  const category = (await page.locator(".categories-block a").first().textContent())?.trim();
  expect(category, "the home page should link to categories").toBeTruthy();
  return category!;
}

// Count the records in a CSV, minding newlines inside quoted values
function countCsvRecords(csv: string): number {
  let records = 0;
  let quoted = false;
  for (const char of csv) {
    if (char === '"') quoted = !quoted;
    else if (char === "\n" && !quoted) records++;
  }
  return records;
}

test.describe("incident export", { tag: ["@qa", "@export"] }, () => {
  test.beforeEach(async ({}, testInfo) => {
    // The export is generated server-side and the download menu is plain HTML,
    // so there's no need to run these in every browser.
    const [firstBrowser] = testInfo.config.projects;
    test.skip(
      testInfo.project.name !== firstBrowser.name,
      `the export specs run in one browser only (${firstBrowser.name})`,
    );
  });

  test("exports incidents as CSV", async ({ page }) => {
    // Get the first category on the homepage and go to its all-incidents page
    const category = await firstCategory(page);
    await page.goto(`${INCIDENTS}?categories=${encodeURIComponent(category)}`);

    // Open the download menu and get the number of incidents it says it has
    await page.locator("summary", { hasText: "Download dataset" }).click();
    const link = page.getByRole("link", { name: /Download your filtered data/ });
    const count = Number(
      (await link.locator(".incident-index__incident-count").textContent())?.replace(/\D/g, ""),
    );
    expect(count, `${category} should have incidents to export`).toBeGreaterThan(0);

    // Download it
    const downloading = page.waitForEvent("download");
    await link.click();
    const download = await downloading;
    expect(download.suggestedFilename()).toBe("incidents.csv");

    // It has a header row, and one row per incident
    const csv = await readFile(await download.path(), "utf8");
    expect(csv.split("\n", 1)[0], "the CSV should have a header row").toContain("title");
    expect(countCsvRecords(csv), "the CSV should have a row per incident").toBe(count + 1);
  });

  test("exports incidents as JSON", async ({ page }) => {
    // Get the first category on the homepage and go to its all-incidents page
    const category = await firstCategory(page);
    const params = `categories=${encodeURIComponent(category)}`;

    // The number of incidents the database has for the category
    const summary = await (await page.request.get(`${INCIDENTS}summary/?${params}`)).json();
    const total = summary.total;
    expect(total, `${category} should have incidents to export`).toBeGreaterThan(0);

    const response = await page.request.get(`${INCIDENTS}export/?format=json&${params}`);
    expect(response.ok(), "the JSON export should respond").toBe(true);
    expect(response.headers()["content-type"]).toContain("application/json");

    // Every incident is exported, and every one is in the category
    const incidents: { title: string; categories: string }[] = await response.json();
    expect(incidents).toHaveLength(total);
    for (const incident of incidents) {
      expect(incident.categories, `"${incident.title}" categories`).toContain(category);
    }
  });
});
