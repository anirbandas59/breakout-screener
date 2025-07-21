import { test, expect } from '@playwright/test';

test.describe('Basic Navigation', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check if the main heading is visible
    await expect(page.getByText('Breakout Screener V2')).toBeVisible();
    
    // Check if the header contains navigation elements
    await expect(page.getByRole('banner')).toBeVisible();
  });

  test('should display theme toggle button', async ({ page }) => {
    await page.goto('/');
    
    // Look for theme toggle button
    const themeToggle = page.getByRole('button').filter({ hasText: /toggle theme/i });
    await expect(themeToggle.first()).toBeVisible();
  });

  test('should handle theme switching', async ({ page }) => {
    await page.goto('/');
    
    // Find and click theme toggle
    const themeToggle = page.getByRole('button').filter({ hasText: /toggle theme/i });
    await themeToggle.first().click();
    
    // Verify theme changed by checking for dark mode class or styling
    // This may require checking the document class or computed styles
    await page.waitForTimeout(500); // Allow animation to complete
  });

  test('should have responsive layout', async ({ page }) => {
    await page.goto('/');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByText('Breakout Screener V2')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.getByText('Breakout Screener V2')).toBeVisible();
  });

  test('should have proper page title', async ({ page }) => {
    await page.goto('/');
    
    await expect(page).toHaveTitle(/Breakout Screener/);
  });
});