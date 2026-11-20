import { test, expect } from "@playwright/test";

// Category page tests, originating with our QA checklist item:
//
//  "Verify category pages load correctly"

test.describe("category pages", { tag: ["@qa", "@category"] }, () => {
  test("every category page loads", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const links = page.locator(".categories-block a");
    const categories = await links.evaluateAll((anchors) =>
      anchors.map((a) => ({
        title: a.textContent?.trim() ?? "",
        href: a.getAttribute("href") ?? "",
      })),
    );
    expect(categories.length, "the home page should link to categories").toBeGreaterThan(0);

    // Loop through categories found on the homepage
    for (const { title, href } of categories) {
      await test.step(title, async () => {
        const response = await page.goto(href);
        // The category loads
        expect(response?.ok(), `${href} should load`).toBe(true);

        // Has a title and total incident count
        await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();
        await expect(page.locator(".categorypage-count")).toContainText(/Total Incidents: \d+/);

        // Lists some recent incidents
        const recents = page
          .locator("section")
          .filter({ has: page.getByRole("heading", { name: "Recent Incidents" }) })
          .locator(".incident-card");
        await expect(recents, `${title} should list its recent incidents`).not.toHaveCount(0);

        // If the category has its chart turned on, it should load its data and
        // draw an svg rect for each year
        const chart = page.locator(".js-categorypage-charts");
        if (await chart.count()) {
          await expect(
            chart.locator("svg rect"),
            `the ${title} chart should draw bars for its incidents`,
          ).not.toHaveCount(0);
        }
      });
    }
  });
});
