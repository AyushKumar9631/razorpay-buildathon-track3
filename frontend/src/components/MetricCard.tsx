import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  format?: 'currency' | 'number' | 'percent';
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

export default function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  format = 'number',
  trend = 'neutral',
  color = 'blue',
}: MetricCardProps) {
  const formatValue = (val: string | number): string => {
    const numVal = typeof val === 'string' ? parseFloat(val) : val;

    switch (format) {
      case 'currency':
        return formatCurrency(numVal);
      case 'percent':
        return formatPercent(numVal);
      case 'number':
      default:
        return formatNumber(numVal);
    }
  };

  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            {formatValue(value)}
          </p>
          {change !== undefined && (
            <p className={cn('text-sm mt-2', trendColor)}>
              {change > 0 ? '+' : ''}{change}% from last period
            </p>
          )}
        </div>
        <div className={cn('p-3 rounded-full', `bg-${color}-100`)}>
          <Icon className={cn('w-6 h-6', `text-${color}-600`)} />
        </div>
      </div>
    </div>
  );
}
