/**
 * Utility functions for formatting and data manipulation
 */

/**
 * Format a number as currency (Indian Rupees)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a number with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Format a percentage
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * Format a date relative to now (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a full date
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get color class based on status
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'text-orange-600 bg-orange-100',
    recovered: 'text-green-600 bg-green-100',
    lost: 'text-red-600 bg-red-100',
    pending: 'text-yellow-600 bg-yellow-100',
    executed: 'text-blue-600 bg-blue-100',
    failed: 'text-red-600 bg-red-100',
    success: 'text-green-600 bg-green-100',
  };
  return colors[status.toLowerCase()] || 'text-gray-600 bg-gray-100';
}

/**
 * Get color class based on priority
 */
export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    high: 'text-red-600 bg-red-100',
    medium: 'text-orange-600 bg-orange-100',
    low: 'text-blue-600 bg-blue-100',
    critical: 'text-purple-600 bg-purple-100',
  };
  return colors[priority.toLowerCase()] || 'text-gray-600 bg-gray-100';
}

/**
 * Get color class based on risk level
 */
export function getRiskColor(risk: string): string {
  const colors: Record<string, string> = {
    high: 'text-red-600 bg-red-100',
    medium: 'text-orange-600 bg-orange-100',
    low: 'text-blue-600 bg-blue-100',
    critical: 'text-purple-600 bg-purple-100',
  };
  return colors[risk.toLowerCase()] || 'text-gray-600 bg-gray-100';
}

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Combine CSS class names
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
