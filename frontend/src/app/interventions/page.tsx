'use client';

import { useEffect, useState } from 'react';
import { getInterventions } from '@/lib/api';
import { Intervention } from '@/types';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import Badge from '@/components/Badge';
import Link from 'next/link';
import { Zap, Loader2 } from 'lucide-react';

export default function InterventionsPage() {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchInterventions();
  }, [filter]);

  const fetchInterventions = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await getInterventions(params);
      setInterventions(data.interventions || []);
    } catch (error) {
      console.error('Error fetching interventions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="animate-spin h-12 w-12 text-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Interventions</h1>
        <p className="text-gray-600 mt-2">Review and manage recovery interventions</p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex space-x-2">
        {['all', 'pending', 'executed', 'failed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === status
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {/* Interventions Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Channel
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Scheduled
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {interventions.map((intervention) => (
              <tr key={intervention.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <Zap className="w-5 h-5 text-purple-500 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {intervention.intervention_type}
                      </p>
                      <p className="text-xs text-gray-500">{intervention.intervention_strategy}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <Badge variant="status" value={intervention.channel || 'email'}>
                    {intervention.channel || 'email'}
                  </Badge>
                </td>
                <td className="px-6 py-4">
                  <Badge variant="status" value={intervention.status}>
                    {intervention.status}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {intervention.scheduled_at
                    ? formatRelativeTime(intervention.scheduled_at)
                    : 'Not scheduled'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {interventions.length === 0 && (
          <div className="text-center py-12">
            <Zap className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No interventions found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'all' ? 'Process risks with AI to create interventions' : `No ${filter} interventions`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
