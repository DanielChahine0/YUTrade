// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.4)
//
// TODO: Client-side validation helpers.
//
// isYorkUEmail(email: string): boolean
//   - Return true if email ends with "@my.yorku.ca" or "@yorku.ca"
//   - Case-insensitive check
//   - Used on RegisterPage to validate before submitting
//
// isValidPassword(password: string): { valid: boolean; message: string }
//   - Min 8 characters
//   - Return { valid: false, message: "Password must be at least 8 characters" } if too short
//   - Return { valid: true, message: "" } if OK
//
// isValidPrice(price: string | number): boolean
//   - Must be a number > 0
//   - Used on CreateListingPage
//
// formatPrice(price: number): string
//   - Return price formatted as "$XX.XX"
//   - e.g. formatPrice(25) -> "$25.00"
//
// formatDate(isoString: string): string
//   - Convert ISO datetime string to human-readable format
//   - e.g. "Feb 22, 2026" or "2 hours ago" (relative time)
//   - Used across ListingCard, ListingDetailPage, MessageThread

export const isYorkUEmail = (email: string): boolean => {
  const emailLower = email.toLowerCase();
  return emailLower.endsWith("@yorku.ca") || emailLower.endsWith("@my.yorku.ca");
};

/**
 * Validates password strength requirements.
 */
export const isValidPassword = (password: string): { valid: boolean; message: string } => {
  if (password.length < 8) {
    return { valid: false, message: "Password must be at least 8 characters" };
  }
  return { valid: true, message: "" };
};

/**
 * Ensures the price is a valid number greater than zero.
 */
export const isValidPrice = (price: string | number): boolean => {
  const num = typeof price === "string" ? parseFloat(price) : price;
  return !isNaN(num) && num > 0;
};

/**
 * Formats a number as a currency string.
 * Example: 25 -> "$25.00"
 */
export const formatPrice = (price: number): string => {
  return `$${price.toFixed(2)}`;
};

/**
 * Converts ISO datetime string to a human-readable format.
 * Example: "2026-02-22T..." -> "Feb 22, 2026"
 */
export const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  
  // Return "Invalid Date" if parsing fails
  if (isNaN(date.getTime())) return "N/A";

  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  // Relative time logic
  if (diffInSeconds < 60) return "Just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;

  // Standard format for older dates
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};
