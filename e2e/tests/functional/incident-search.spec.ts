import { test, expect } from "@playwright/test";

// Incident search tests, originating with our QA checklist items:
//
//  "Verify categories based filtering works"
//  "Verify search box features are functional"

const INCIDENTS = "/all-incidents/";

// String that is unlikely to appear in any incident
const NO_MATCH = "zqxjkvw";

test.describe("incident search box", { tag: ["@qa", "@search"] }, () => {
  test("finds an incident by a word in its title", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    const titles = page.locator(".incident-database-card__title");

    // Get the longest word in the first listed incident's title (it's
    // unlikely to be a stop word)
    const title = (await titles.first().textContent())?.replace(/\s+/g, " ").trim() ?? "";
    expect(title, "the database should list incidents").toBeTruthy();
    const word = title
      .split(" ")
      .map((w) => w.replace(/\W/g, ""))
      .reduce((a, b) => (b.length > a.length ? b : a));

    // Search for that word
    const search = page.getByLabel("Search incidents by text");
    await search.fill(word);
    await search.press("Enter");

    // There should be results
    await expect(page).toHaveURL(new RegExp(`[?&]search=${word}`));
    await expect(
      titles.filter({ hasText: title }),
      `searching "${word}" should find "${title}"`,
    ).not.toHaveCount(0);
  });

  test("reports when nothing matches", async ({ page }) => {
    // Search for a string that *shouldn't* match anything
    await page.goto(`${INCIDENTS}?search=${NO_MATCH}`, { waitUntil: "domcontentloaded" });

    // And it tells us there are no results for that string
    await expect(
      page.locator(".incident-index__body-header-controls .paragraph-subtitle"),
    ).toContainText(`0 incidents recorded for ‘${NO_MATCH}’`);

    // And there truly aren't any
    await expect(page.locator(".incident-database-card")).toHaveCount(0);
  });
});

test.describe("incident category filter", { tag: ["@qa", "@search"] }, () => {
  test("lists only incidents in the chosen category", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });

    // Toggle the filters (on mobile)
    const toggle = page.getByRole("button", { name: "Filters", exact: true });
    if (await toggle.isVisible()) await toggle.click();

    // Find the first category that has incidents and get its checkbox,
    // symbol, and title
    const category = page.locator(".category-checkbox:not(.category-checkbox--disabled)").first();
    const category_checkbox = category.locator(".category-checkbox--input");
    const category_symbol = await category_checkbox.getAttribute("id");
    const category_title = (await category.locator("label .category").textContent())?.trim();

    // Click on the category, ensure it's selected
    await category.locator("label").click();
    await expect(category_checkbox, `${category_title} should be selected`).toBeChecked();

    // Apply the category filter
    await page.getByRole("button", { name: "Apply filters" }).filter({ visible: true }).first().click();

    // The category should be in the filter summary
    await expect(
      page.locator("#filter-summary").getByLabel(`Removes filter: ${category_title?.toLowerCase()}`),
      `${category_title} should be in the filter summary`,
    ).toBeVisible();

    // And cards should exist and should all belong to that category
    const cards = page.locator(".incident-database-card");
    await expect(cards, `${category_title} should have incidents`).not.toHaveCount(0);
    await expect(
      cards.filter({ hasNot: page.locator(`.category-${category_symbol}`) }),
      `every incident listed should be in ${category_title}`,
    ).toHaveCount(0);
  });
});
