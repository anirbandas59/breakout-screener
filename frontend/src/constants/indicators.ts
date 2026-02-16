/**
 * Indicator constants — mirror of Python BreakoutIndicator, CandleIndicator,
 * and VolumeIndicator enums in app/models/enums.py.
 *
 * These values must match the enum .value strings exactly. If the backend enums
 * change, update this file accordingly (or use the generated types from /api/enums).
 */

// ========================
// Breakout Indicator
// ========================

export const BREAKOUT_INDICATOR = {
  RED_CANDLE: 'Red candle',
  NO_BREAKOUT: 'no breakout',
  BREAKOUT: 'Breakout',
  BIG_SELL_WICK: 'Big Sell Wick',
  NO_ENTRY: 'No Entry',
} as const;

export type BreakoutIndicatorValue =
  (typeof BREAKOUT_INDICATOR)[keyof typeof BREAKOUT_INDICATOR];

/** All breakout indicator display values — use for filter dropdowns. */
export const BREAKOUT_FILTER_OPTIONS: BreakoutIndicatorValue[] = Object.values(
  BREAKOUT_INDICATOR
);

// ========================
// Candle Indicator
// ========================

export const CANDLE_INDICATOR = {
  RED_CANDLE: 'Red candle',
  GREEN_CANDLE: 'Green candle',
  DOJI: 'Doji',
} as const;

export type CandleIndicatorValue =
  (typeof CANDLE_INDICATOR)[keyof typeof CANDLE_INDICATOR];

// ========================
// Volume Indicator
// ========================

export const VOLUME_INDICATOR = {
  GOOD: 'Good',
  AVERAGE: 'Average',
  LOW: 'Low',
} as const;

export type VolumeIndicatorValue =
  (typeof VOLUME_INDICATOR)[keyof typeof VOLUME_INDICATOR];

// ========================
// Badge variant helper
// ========================

/**
 * Map an indicator value to a badge display variant.
 * Extracted from DataTable.tsx to centralise indicator display logic.
 */
export function getIndicatorVariant(
  value: string | null | undefined,
  type: 'breakout' | 'candle' | 'volume'
): 'success' | 'warning' | 'danger' | 'default' {
  if (!value) return 'default';

  const normalized = value.toLowerCase().trim();

  if (type === 'breakout') {
    if (normalized === BREAKOUT_INDICATOR.BREAKOUT.toLowerCase()) return 'success';
    if (normalized === BREAKOUT_INDICATOR.RED_CANDLE.toLowerCase()) return 'warning';
    if (normalized === BREAKOUT_INDICATOR.NO_BREAKOUT.toLowerCase()) return 'default';
    if (normalized === BREAKOUT_INDICATOR.BIG_SELL_WICK.toLowerCase()) return 'danger';
    if (normalized === BREAKOUT_INDICATOR.NO_ENTRY.toLowerCase()) return 'default';
  } else if (type === 'candle') {
    if (normalized === CANDLE_INDICATOR.GREEN_CANDLE.toLowerCase()) return 'success';
    if (normalized === CANDLE_INDICATOR.RED_CANDLE.toLowerCase()) return 'danger';
    if (normalized === CANDLE_INDICATOR.DOJI.toLowerCase()) return 'warning';
  } else if (type === 'volume') {
    if (normalized === VOLUME_INDICATOR.GOOD.toLowerCase()) return 'success';
    if (normalized === VOLUME_INDICATOR.AVERAGE.toLowerCase()) return 'warning';
    if (normalized === VOLUME_INDICATOR.LOW.toLowerCase()) return 'danger';
  }

  return 'default';
}
