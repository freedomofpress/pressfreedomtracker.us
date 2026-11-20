import { test, expect } from "@playwright/test";

// Homepage tests, originating with our QA checklist items:
//
//  "Verify that it renders correctly in homepage"
//  "Verify that visualizations using the API endpoints are functional"

test.describe("homepage", { tag: ["@qa", "@homepage"] }, () => {
  test("charts load their data", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    // The category chart links each category to the incident database, once
    // the incidents and categories have loaded from the API
    const categoryChart = page.locator(".hpChart", {
      has: page.locator("#homepage-treemap-chart-label"),
    });
    await expect(
      categoryChart.getByRole("link"),
      "the category chart should show categories",
    ).not.toHaveCount(0);
  });

  test("lists featured and recent incidents, and featured posts", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.locator("#featured-incidents-carousel .incident-card")).not.toHaveCount(0);
    await expect(page.locator(".article-carousel__item--latest .incident-card")).not.toHaveCount(0);
    await expect(page.locator("#featured-blogs-carousel .blog-card")).not.toHaveCount(0);
  });
});
