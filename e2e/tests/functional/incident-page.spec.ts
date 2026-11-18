import { test, expect } from "@playwright/test";

// Incident page tests, originating with our QA checklist item:
//
//  "Verify that it renders correctly in individual incident page"

const INCIDENTS = "/all-incidents/";

test.describe("incident page", { tag: ["@qa", "@incident"] }, () => {
  test("shows its details", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });

    // Open the first incident listed
    const card = page.locator(".incident-database-card").first();
    const title = (await card.locator(".incident-database-card__title").textContent())!
      .replace(/\s+/g, " ")
      .trim();
    await card.locator(".incident-database-card__title-link").click();

    await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();

    // It has incident details and details for each of its categories
    const details = page.locator(".details-table");
    await expect(details).toContainText("Date of incident");
    await expect(details.locator(".details-table__category-fields")).not.toHaveCount(0);

    // And it has a body
    await expect(page.locator(".article-content__inner")).not.toBeEmpty();
  });
});
