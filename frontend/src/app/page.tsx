'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, DollarSign, AlertTriangle, Zap, Clock, Target } from 'lucide-react';
import MetricCard from '@/components/MetricCard';
import { getAnalyticsOverview, getRisks } from '@/lib/api';
import { AnalyticsOverview, Risk } from '@/types';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import Badge from '@/components/Badge';
import Link from 'next/link';

export default function Dashboard() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recentRisks, setRecentRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewData, risksData] = await Promise.all([
          getAnalyticsOverview(),
          getRisks({ limit: 5 }),
        ]);
        setOverview(overviewData);
        setRecentRisks(risksData.risks || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="mb-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">Loading dashboard data...</p>
          <p className="text-gray-500 text-xs mt-2">⏳ Render free tier may take 30-60 seconds on first load. Please be patient.</p>
        </div>

        {/* Skeleton Loading */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-300 rounded w-3/4"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-100 rounded"></div>
              ))}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-64 bg-gray-100 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">AI-powered revenue recovery overview</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Revenue at Risk"
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

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Risks */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Risks</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {recentRisks.length > 0 ? (
              recentRisks.map((risk) => (
                <Link
                  key={risk.id}
                  href={`/risks/${risk.id}`}
                  className="p-4 hover:bg-gray-50 block transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge variant="priority" value={risk.priority}>
                          {risk.priority}
                        </Badge>
                        <Badge variant="status" value={risk.status}>
                          {risk.status}
                        </Badge>
                      </div>
                      <p className="text-sm font-medium text-gray-900">
                        {risk.risk_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {risk.customer_email}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatRelativeTime(risk.detected_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {formatCurrency(risk.risk_amount)}
                      </p>
                      {risk.risk_score && (
                        <p className="text-xs text-gray-600 mt-1">
                          Score: {risk.risk_score}%
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No recent risks
              </div>
            )}
          </div>
          <div className="p-4 border-t border-gray-200">
            <Link
              href="/risks"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View all risks →
            </Link>
          </div>
        </div>

        {/* 24h Activity */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Last 24 Hours</h2>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">New Risks</p>
                    <p className="text-xs text-gray-600">Detected in last 24h</p>
                  </div>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {overview?.last_24h?.new_risks || 0}
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <DollarSign className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">Recovered</p>
                    <p className="text-xs text-gray-600">Successfully recovered</p>
                  </div>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {overview?.last_24h?.recovered || 0}
                </p>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600">Recovery success rate</p>
                  <p className="text-lg font-semibold text-green-600">
                    {overview?.recovery_rate?.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/risks"
            className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <div>
              <p className="font-medium text-gray-900">View All Risks</p>
              <p className="text-sm text-gray-600">Manage revenue at risk</p>
            </div>
            <AlertTriangle className="w-5 h-5 text-gray-400" />
          </Link>

          <Link
            href="/interventions"
            className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all"
          >
            <div>
              <p className="font-medium text-gray-900">Interventions</p>
              <p className="text-sm text-gray-600">Review and execute</p>
            </div>
            <Zap className="w-5 h-5 text-gray-400" />
          </Link>

          <Link
            href="/analytics"
            className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all"
          >
            <div>
              <p className="font-medium text-gray-900">Analytics</p>
              <p className="text-sm text-gray-600">View detailed reports</p>
            </div>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </Link>
        </div>
      </div>
    </div>
  );
}
