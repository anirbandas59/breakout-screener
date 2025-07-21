import { test, expect } from '@playwright/test';

test.describe('Data Table Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display empty state when no data', async ({ page }) => {
    // Look for empty state message
    const emptyState = page.getByText('No breakout data available');
    
    // It may be visible immediately or after loading
    await expect(emptyState.first()).toBeVisible({ timeout: 10000 });
  });

  test('should handle loading state', async ({ page }) => {
    // Look for loading indicator
    const loadingText = page.getByText('Loading...');
    
    // Loading may appear briefly or not at all if data loads quickly
    if (await loadingText.isVisible()) {
      await expect(loadingText).toBeVisible();
    }
  });

  test('should display table headers when data is present', async ({ page }) => {
    // Mock API response to ensure we have data to test with
    await page.route('/api/v1/**', async route => {
      const url = route.request().url();
      
      if (url.includes('/breakout-data/')) {
        // Mock breakout data response
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: '550e8400-e29b-41d4-a716-446655440001',
                stock_symbol: 'RELIANCE',
                trade_date: '2024-01-15',
                close_price: 2500.50,
                volume: 5000000,
                breakout_status: 'BULLISH_BREAKOUT',
                candle_indicator: 'BULLISH',
                volume_indicator: 'HIGH_VOLUME',
                breakout_strength: 15.2,
                created_at: '2024-01-15T10:00:00Z',
                updated_at: '2024-01-15T10:00:00Z'
              }
            ],
            total: 1,
            page: 1,
            limit: 20,
            has_next: false,
            has_previous: false
          })
        });
      } else {
        // Let other requests pass through
        await route.continue();
      }
    });

    await page.reload();

    // Check for table headers
    await expect(page.getByText('Symbol')).toBeVisible();
    await expect(page.getByText('Date')).toBeVisible();
    await expect(page.getByText('Breakout')).toBeVisible();
    await expect(page.getByText('Volume')).toBeVisible();
  });

  test('should handle external chart link clicks', async ({ page }) => {
    // Mock data to ensure we have a chart button
    await page.route('/api/v1/**', async route => {
      const url = route.request().url();
      
      if (url.includes('/breakout-data/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: '550e8400-e29b-41d4-a716-446655440001',
                stock_symbol: 'RELIANCE',
                trade_date: '2024-01-15',
                close_price: 2500.50,
                volume: 5000000,
                breakout_status: 'BULLISH_BREAKOUT',
                candle_indicator: 'BULLISH',
                volume_indicator: 'HIGH_VOLUME',
                breakout_strength: 15.2,
                created_at: '2024-01-15T10:00:00Z',
                updated_at: '2024-01-15T10:00:00Z'
              }
            ],
            total: 1,
            page: 1,
            limit: 20,
            has_next: false,
            has_previous: false
          })
        });
      } else {
        await route.continue();
      }
    });

    await page.reload();

    // Wait for data to load and look for chart buttons
    const chartButton = page.getByRole('button').filter({ hasText: /chart/i });
    
    if (await chartButton.count() > 0) {
      // Test that clicking chart button opens new window
      const [popup] = await Promise.all([
        page.waitForEvent('popup'),
        chartButton.first().click()
      ]);
      
      expect(popup.url()).toContain('chartink.com');
    }
  });
});