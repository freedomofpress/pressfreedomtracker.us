import { test, expect, type Page } from "@playwright/test";

// Incident filter tests, originating with our QA checklist item:
//
//  "Verify all the filters in Incident Search page works"
//
// Each kind of filter has its own widget in the sidebar, and its own way of
// being written into the URL, so there's one test per *kind* rather than per
// filter.
//
// Each test uses the first filter of its kind the sidebar offers, so
// they work against the QA data and deployed environments alike.
//
// A filter is considered working when applying it shows it in the filter
// summary, not when there are results.

const INCIDENTS = "/all-incidents/";

// The sidebar is built from a list of filter groups, serialized into its
// data-serialized-filters attribute: "General" first, then one per category.
type FilterGroup = {
  id: number; // -1 for "General", otherwise the category's id
  symbol?: string; // the category's symbol, which is its checkbox's id
  filters: Filter[];
};

type Filter = {
  name: string;
  type: string;
  choices?: string[];
  present_summary_name?: string;
};

// Open the filter sidebar, which on mobile is behind a toggle
async function openSidebar(page: Page) {
  const toggle = page.getByRole("button", { name: "Filters", exact: true });
  if (await toggle.isVisible()) await toggle.click();
}

// Find the first filter of the given type in the open sidebar, ticking its
// category if it belongs to one so the filter shows.
async function openFilter(page: Page, type: string): Promise<Filter> {
  const json = await page.locator("#filter-sidebar").getAttribute("data-serialized-filters");
  const groups: FilterGroup[] = JSON.parse(json ?? "[]");

  for (const group of groups) {
    for (const filter of group.filters) {
      // Search and tags have widgets of their own, elsewhere
      if (filter.name === "search" || filter.name === "tags") continue;
      if (filter.type !== type) continue;

      // Category filters only show once their category is selected
      if (group.id !== -1) {
        await page.locator(`label[for="${group.symbol}"]`).click();
        await expect(page.locator(`#${group.symbol}`)).toBeChecked();
      }

      return filter;
    }
  }

  throw new Error(`the sidebar should have a ${type} filter`);
}

async function applyFilters(page: Page) {
  await page.getByRole("button", { name: "Apply filters" }).filter({ visible: true }).first().click();
}

test.describe("incident filters", { tag: ["@qa", "@search"] }, () => {
  test("text filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "text");
    await page.locator(`#id_${filter.name}`).fill("Springfield");
    await applyFilters(page);

    await expect(page.locator("#filter-summary")).toContainText("Springfield", { ignoreCase: true });
  });

  test("date filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "date");
    await page.locator(`#id_${filter.name}_after`).fill("2020-01-01");
    await applyFilters(page);

    await expect(page.locator("#filter-summary")).toContainText("2020-01-01");
  });

  test("autocomplete filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "autocomplete");
    // One of the filter's suggestions, or anything if it has none
    const value = filter.choices?.[0] ?? "QA";
    await page.locator(`#id_${filter.name}`).fill(value);
    await applyFilters(page);

    await expect(page.locator("#filter-summary")).toContainText(value, { ignoreCase: true });
  });

  test("choice filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "choice");
    const select = page.locator(`#id_${filter.name}`);
    // The first option is the empty "------", so pick the one after it
    await select.selectOption({ index: 1 });
    const value = await select.inputValue();
    await applyFilters(page);

    // The summary shows choices with spaces for underscores
    await expect(page.locator("#filter-summary")).toContainText(value.replaceAll("_", " "), {
      ignoreCase: true,
    });
  });

  test("yes/no filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "bool");
    // The "Yes" option
    await page.locator(`#id_${filter.name}_0`).check();
    await applyFilters(page);

    // Yes/no filters are summarized with a phrase of their own
    await expect(page.locator("#filter-summary")).toContainText(filter.present_summary_name!);
  });

  test("yes/no/unknown filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);
    const filter = await openFilter(page, "radio");
    // The "Yes" option, after "Unknown"
    await page.locator(`#id_${filter.name}_1`).check();
    await applyFilters(page);

    await expect(page.locator("#filter-summary")).toContainText("just true");
  });

  test("tag filter", async ({ page }) => {
    await page.goto(INCIDENTS, { waitUntil: "domcontentloaded" });
    await openSidebar(page);

    // Open the tag section (if it isn't already), and select its first tag
    // (labelled "#tag")
    const tags = page.locator("details", { has: page.getByRole("heading", { name: "Tag", exact: true }) });
    if (!(await tags.evaluate((details: HTMLDetailsElement) => details.open))) {
      await tags.locator("summary").click();
    }
    const label = tags.locator("label", { hasText: /^#/ }).first();
    const tag = (await label.textContent())!.trim().slice(1);
    await label.click();
    await applyFilters(page);

    await expect(page.locator("#filter-summary")).toContainText(tag, { ignoreCase: true });
  });
});
