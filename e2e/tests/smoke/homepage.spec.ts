import { test, expect } from "@playwright/test";

test.describe("homepage", () => {
  test("renders", { tag: ["@smoke"] }, async ({ page }) => {
    const response = await page.goto("/");
    expect(response?.ok()).toBe(true);

    await expect(
      page.getByRole("heading", { level: 1, name: "The U.S. Press Freedom Tracker" }),
    ).toBeVisible();

    // Has the site summary seeded by createqadata
    await expect(page.locator(".site-summary")).toContainText("press freedom incidents");

    // Has navigation
    await expect(page.getByRole("navigation").first()).toBeAttached();
  });
});
