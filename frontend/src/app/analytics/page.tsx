'use client';

import { useEffect, useState } from 'react';
import { getAnalyticsOverview } from '@/lib/api';
import { AnalyticsOverview } from '@/types';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { TrendingUp, DollarSign, Target, Clock, Zap, AlertTriangle } from 'lucide-react';
import MetricCard from '@/components/MetricCard';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const data = await getAnalyticsOverview();
      setOverview(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">Comprehensive revenue recovery insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Total Revenue at Risk"
          value={overview?.total_revenue_at_risk || 0}
          format="currency"
          icon={AlertTriangle}
          color="orange"
        />
        <MetricCard
          title="Revenue Recovered"
          value={overview?.total_revenue_recovered || 0}
          format="currency"
          icon={DollarSign}
          color="green"
          trend="up"
        />
        <MetricCard
          title="Recovery Rate"
          value={overview?.recovery_rate || 0}
          format="percent"
          icon={TrendingUp}
          color="blue"
        />
        <MetricCard
          title="Active Risks"
          value={overview?.active_risks || 0}
          format="number"
          icon={Target}
          color="red"
        />
        <MetricCard
          title="Active Interventions"
          value={overview?.active_interventions || 0}
          format="number"
          icon={Zap}
          color="purple"
        />
        <MetricCard
          title="Avg Recovery Time"
          value={`${(overview?.avg_recovery_time_hours || 0).toFixed(1)}h`}
          icon={Clock}
          color="indigo"
        />
      </div>

      {/* Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Priority */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risks by Priority</h2>
          <div className="space-y-4">
            {overview?.by_priority && Object.entries(overview.by_priority).map(([priority, count]) => (
              <div key={priority} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    priority === 'high' ? 'bg-red-500' :
                    priority === 'medium' ? 'bg-orange-500' :
                    'bg-blue-500'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700 capitalize">{priority}</span>
                </div>
                <span className="text-sm font-semibold text-gray-900">{count}</span>
              </div>
            ))}
            {(!overview?.by_priority || Object.keys(overview.by_priority).length === 0) && (
              <p className="text-sm text-gray-500 text-center py-4">No priority data available</p>
            )}
          </div>
        </div>

        {/* By Type */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risks by Type</h2>
          <div className="space-y-4">
            {overview?.by_type && Object.entries(overview.by_type).map(([type, data]: [string, any]) => (
              <div key={type} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">
                    {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                  <p className="text-xs text-gray-500">{formatCurrency(data.amount)}</p>
                </div>
                <span className="text-sm font-semibold text-gray-900">{data.count}</span>
              </div>
            ))}
            {(!overview?.by_type || Object.keys(overview.by_type).length === 0) && (
              <p className="text-sm text-gray-500 text-center py-4">No type data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Last 24 Hours */}
      <div className="mt-6 bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Last 24 Hours Activity</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-orange-600">{overview?.last_24h?.new_risks || 0}</p>
            <p className="text-sm text-gray-600 mt-1">New Risks Detected</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{overview?.last_24h?.recovered || 0}</p>
            <p className="text-sm text-gray-600 mt-1">Successfully Recovered</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">
              {overview?.recovery_rate ? `${overview.recovery_rate.toFixed(1)}%` : '0%'}
            </p>
            <p className="text-sm text-gray-600 mt-1">Success Rate</p>
          </div>
        </div>
      </div>
    </div>
  );
}
