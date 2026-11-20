import { test, expect, type Page } from "@playwright/test";

// Incident submission form tests, originating with our QA checklist item:
//
//  "Verify "Submit an Incident" form submits without errors"
//
// These don't submit the form: a deployed environment would send it on to
// real people, behind a real reCAPTCHA. They check that the form is there, is
// protected by reCAPTCHA, and that the browser won't send it incomplete.

// Go to the incident form, by way of the header's "Submit an Incident" link.
// The link is in the navigation menu on mobile, so we follow its href rather
// than clicking it.
async function goToIncidentForm(page: Page) {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  const href = await page
    .locator("#secondary-navigation a", { hasText: "Submit an Incident" })
    .getAttribute("href");
  expect(href, "the header should link to the incident form").toBeTruthy();

  const response = await page.goto(href!);
  expect(response?.ok(), `${href} should load`).toBe(true);
}

test.describe("incident form", { tag: ["@qa", "@forms"] }, () => {
  test("renders", async ({ page }) => {
    await goToIncidentForm(page);

    const form = page.locator("form.form");
    await expect(form.locator(".form-field").first()).toBeVisible();
    await expect(form.locator("button[type='submit']")).toBeVisible();
  });

  test("loads reCAPTCHA", async ({ page }) => {
    // The local QA stack has no reCAPTCHA keys
    test.skip(!process.env.E2E_ENV, "reCAPTCHA only loads in a deployed environment");

    await goToIncidentForm(page);

    await expect(page.locator("form.form iframe[title='reCAPTCHA']")).toBeVisible();
  });

  test("blocks an incomplete submission in the browser", async ({ page }) => {
    await goToIncidentForm(page);
    const form = page.locator("form.form");
    const url = page.url();

    // The browser only stops a submission for required fields, so without
    // any, this would send a blank submission
    await expect(form.locator("[required]"), "the form should have required fields").not.toHaveCount(0);

    await form.locator("button[type='submit']").click();

    // The browser flags the required fields, and doesn't send it
    await expect(form.locator(":invalid")).not.toHaveCount(0);
    expect(page.url()).toBe(url);
  });
});
