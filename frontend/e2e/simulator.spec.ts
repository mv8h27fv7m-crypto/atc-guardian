import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page, request }) => {
  await request.post("/api/scenario", { data: { scenario: "missed_turn" } });
  await page.goto("/");
  await expect(
    page.getByText("SIMULATOR CONNECTED", { exact: true }),
  ).toBeVisible();
});

test("missed turn remains active when acknowledged, then clears after pilot recovery", async ({
  page,
}) => {
  await page.getByRole("button", { name: "+30 sec" }).click();
  await expect(
    page.getByRole("heading", { name: "Turn not detected" }),
  ).toBeVisible();
  const missed = page
    .locator("article.alert")
    .filter({ has: page.getByRole("heading", { name: "Turn not detected" }) });
  await missed
    .getByRole("button", { name: "Acknowledge", exact: true })
    .click();
  await expect(
    missed.getByRole("button", { name: "✓ Acknowledged · still active" }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Pilot requests human", exact: true })
    .click();
  await expect(
    page.getByText("Human review: Pilot requested human"),
  ).toBeVisible();
  await page
    .locator("summary")
    .filter({ hasText: "Simulation fault controls" })
    .click();
  await page
    .getByRole("button", { name: "Restore pilot turn response" })
    .click();
  await page.getByRole("button", { name: "+30 sec" }).click();
  await expect(
    page.getByRole("heading", { name: "Turn not detected" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Restore assistance", exact: true }),
  ).toBeVisible();
});

test("scenario navigation, structured readback correction, and explicit resumption", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Scenario lab", exact: true }).click();
  await page.getByRole("button", { name: /One thousand feet off/ }).click();
  await expect(
    page.getByRole("heading", { name: "Readback requires correction" }),
  ).toBeVisible();
  await page
    .getByText("Propose a simulated clearance", { exact: false })
    .click();
  await page.getByRole("button", { name: "Fill matching text" }).click();
  await page.getByRole("button", { name: "Verify", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Readback requires correction" }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Restore assistance", exact: true })
    .click();
  await expect(page.locator(".ownership")).toHaveText("ASSISTED");
});

test("screens a changed clearance and requires human review before approval", async ({
  page,
}) => {
  await page
    .getByText("Propose a simulated clearance", { exact: false })
    .click();
  await page.getByLabel("Proposed heading").fill("20");
  await page.getByRole("button", { name: "Screen proposal" }).click();
  await expect(page.locator(".preview")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Approve in simulation" }),
  ).toBeDisabled();
  await page.getByLabel("I reviewed these assumptions and findings.").check();
  await page.getByRole("button", { name: "Approve in simulation" }).click();
  await expect(
    page.getByText("AWAITING READBACK", { exact: true }),
  ).toBeVisible();
});

test("stale surveillance has no trajectory and stays human after restoring feed", async ({
  page,
  request,
}) => {
  await request.post("/api/scenario", {
    data: { scenario: "surveillance_loss" },
  });
  await page.getByRole("button", { name: "+30 sec" }).click();
  await expect(
    page.getByRole("heading", { name: "Surveillance unavailable" }),
  ).toBeVisible();
  await page
    .locator("summary")
    .filter({ hasText: "Simulation fault controls" })
    .click();
  await page.getByRole("button", { name: "Restore surveillance" }).click();
  await expect(
    page.getByRole("heading", { name: "Surveillance unavailable" }),
  ).toHaveCount(0);
  await expect(page.locator(".ownership")).toHaveText("HUMAN");
});

test("weather and vector layers toggle, event export is JSON", async ({
  page,
}) => {
  await page.getByLabel("Weather", { exact: true }).uncheck();
  await expect(
    page.locator("svg.scope").getByText("SYNTHETIC ZONE"),
  ).toHaveCount(0);
  await page.getByLabel("Paths", { exact: true }).uncheck();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Export session" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("atc-guardian-events.json");
});

test("mobile layout has no horizontal document overflow or JavaScript errors", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Every aircraft. Always in view." }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});

test("connection loss marks assessment unavailable and disables commands", async ({
  page,
}) => {
  await page.context().setOffline(true);
  await expect(
    page.getByText("CONNECTION UNAVAILABLE", { exact: true }),
  ).toBeVisible({ timeout: 8000 });
  await expect(
    page.getByRole("button", { name: "▶ Run", exact: true }),
  ).toBeDisabled();
  await page.context().setOffline(false);
});
