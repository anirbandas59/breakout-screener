export const getCurrentDate = (): string => {
  /**
   * Get the current date based on the following logic:
   * - Between 6 PM IST and 6 AM IST of the next day: Return the current date.
   * - Between 6 AM IST and 6 PM IST: Return the previous day's date.
   *
   * Returns:
   *   string: Date string in the format YYYY-MM-DD.
   */

  // Get current date and time in UTC
  const nowUtc = new Date();

  // Convert UTC time to IST (UTC + 5:30)
  const offset = 5.5 * 60 * 60 * 1000; // IST offset in milliseconds
  const nowIst = new Date(nowUtc.getTime() + offset);

  // Get current date components in IST
  const year = nowIst.getUTCFullYear();
  const month = nowIst.getUTCMonth(); // Month is 0-indexed
  const date = nowIst.getUTCDate();

  // Define 6 AM and 6 PM in IST
  const sixAmIst = new Date(Date.UTC(year, month, date, 0, 0, 0) + offset + 6 * 60 * 60 * 1000); // 6 AM IST
  const sixPmIst = new Date(Date.UTC(year, month, date, 0, 0, 0) + offset + 18 * 60 * 60 * 1000); // 6 PM IST

  let resultDate: Date;

  // Determine the date to return
  if (nowIst >= sixAmIst && nowIst < sixPmIst) {
    // Between 6 AM and 6 PM IST: Return previous day's date
    resultDate = new Date(nowIst.getTime() - 24 * 60 * 60 * 1000); // Subtract one day
  } else {
    // Between 6 PM and 6 AM IST: Return the current date
    resultDate = nowIst;
  }

  // Format the date in YYYY-MM-DD format
  const formattedDate = resultDate.toISOString().split('T')[0];

  return formattedDate;
};
