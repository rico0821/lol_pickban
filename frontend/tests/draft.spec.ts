import { test, expect } from '@playwright/test';

test('has title and team displays', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page.locator('h1')).toContainText('Draft Screen');

  // Expect team displays to be visible
  await expect(page.getByText('Blue Team')).toBeVisible();
  await expect(page.getByText('Red Team')).toBeVisible();
}); 