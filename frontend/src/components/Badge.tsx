import React from 'react';
import { cn, getRiskColor, getStatusColor } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'priority' | 'status' | 'default';
  value?: string;
  className?: string;
}

export default function Badge({ children, variant = 'default', value, className }: BadgeProps) {
  let colorClass = 'text-gray-600 bg-gray-100';

  if (variant === 'priority' && value) {
    colorClass = getRiskColor(value);
  } else if (variant === 'status' && value) {
    colorClass = getStatusColor(value);
  }

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        colorClass,
        className
      )}
    >
      {children}
    </span>
  );
}
