import { test, expect } from "@playwright/test";

// Footer email signup tests, originating with our QA checklist item:
//
//  "Verify the email signup in footer works"
//
// The signup is sent on to Mailchimp by our server which we can't fake from
// here. Instead, the submission tests mock the browser's request to the
// server so nothing is signed up to and they're safe to run against
// a deployed environment. They test the form and its JavaScript in browser,
// the server's side is covered by the Django tests. So, this may not really
// be an integration or end-to-end test exactly.

const SUBSCRIBE = "**/subscribe_for_site/";

test.describe("email signup", { tag: ["@qa", "@emails"] }, () => {
  test("renders", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const form = page.locator("footer form.emails-signup__form");
    await expect(form.getByLabel("Email address")).toBeVisible();
    await expect(form.getByRole("button", { name: "Sign up" })).toBeVisible();
  });

  test("thanks the visitor for signing up", async ({ page }) => {
    // Answer the signup as a success
    let sent: unknown;
    await page.route(SUBSCRIBE, async (route) => {
      sent = route.request().postDataJSON();
      await route.fulfill({ json: { success: true } });
    });

    await page.goto("/", { waitUntil: "domcontentloaded" });
    const form = page.locator("footer form.emails-signup__form");
    await form.getByLabel("Full Name").fill("QA Tester");
    await form.getByLabel("Email address").fill("qa@example.com");
    await form.getByRole("button", { name: "Sign up" }).click();

    // The form is swapped for a thank you message after successful signup
    await expect(page.locator("#mc-subscribe-thanks")).toContainText("Thanks for subscribing");
    await expect(form).toBeHidden();

    // And the form submission had name and email
    expect(sent).toEqual({ full_name: "QA Tester", email: "qa@example.com" });
  });

  test("tells the visitor when signing up fails", async ({ page }) => {
    // Answer the signup as a failure as if there was an error
    await page.route(SUBSCRIBE, (route) =>
      route.fulfill({ json: { success: false, message: "Error communicating with Mailchimp" } }),
    );

    await page.goto("/", { waitUntil: "domcontentloaded" });
    const form = page.locator("footer form.emails-signup__form");
    await form.getByLabel("Full Name").fill("QA Tester");
    await form.getByLabel("Email address").fill("qa@example.com");
    await form.getByRole("button", { name: "Sign up" }).click();

    await expect(form.getByRole("status")).toHaveText("An internal error occurred.");
  });
});
