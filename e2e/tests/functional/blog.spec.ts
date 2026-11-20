import { test, expect } from "@playwright/test";

// Blog tests originating with our QA checklist items:
//
//  "Verify that the blog index page renders correctly"
//  "Verify that the individual blogs show all the informations correctly"
//  "Verify that it renders correctly in individual special blog page"

const BLOG = "/blog/";

test.describe("blog", { tag: ["@qa", "@blog"] }, () => {
  test("index lists posts", async ({ page }) => {
    const response = await page.goto(BLOG);
    expect(response?.ok(), `${BLOG} should load`).toBe(true);

    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.locator(".blog-list__posts .blog-list__item")).not.toHaveCount(0);
  });

  test("a post shows its details", async ({ page }) => {
    await page.goto(BLOG, { waitUntil: "domcontentloaded" });

    // Open the first regular post listed
    const link = page.locator(".blog-list__posts .blog-card a.text-link--card").first();
    const title = (await link.textContent())!.trim();
    await link.click();

    // It has its title, publication date, author, and a body
    await expect(page.getByRole("heading", { level: 1, name: title })).toBeVisible();
    const details = page.locator(".details-table");
    await expect(details).toContainText("Published On");
    await expect(details).toContainText("Written by");
    await expect(page.locator(".article-content__block")).not.toHaveCount(0);
  });

  test("a special post shows its lead graphic", async ({ page }) => {
    await page.goto(`${BLOG}?type=special`, { waitUntil: "domcontentloaded" });

    // The first special post listed
    const link = page.locator(".special-blog-card a.text-link--card").first();
    const title = (await link.textContent())!.trim();
    const href = (await link.getAttribute("href"))!;

    // Open it, keeping track of the incident data it loads from the API for
    // a chart (only from here, as the listing may load some for itself)
    const loaded: string[] = [];
    page.on("response", (response) => {
      if (response.url().includes("/api/edge/incidents/") && response.ok()) {
        loaded.push(response.url());
      }
    });
    await page.goto(href);

    await expect(page.locator(".special-blog__hero-title")).toHaveText(title);

    // Its lead graphic is an image or a chart.
    // A chart is empty until its data has loaded.
    const hero = page.locator(".special-blog__hero-bg");
    await expect(hero).toBeVisible();
    const chart = hero.locator(".chartContainer");
    if (await chart.count()) {
      await expect(chart.locator("svg > *").first(), "the lead chart should be drawn").toBeAttached();
      expect(loaded, "the lead chart should load incident data").not.toHaveLength(0);
    }
  });
});
