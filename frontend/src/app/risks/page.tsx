'use client';

import { useEffect, useState } from 'react';
import { getRisks, processRisk } from '@/lib/api';
import { Risk } from '@/types';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import Badge from '@/components/Badge';
import Link from 'next/link';
import { AlertTriangle, Loader2, Play } from 'lucide-react';

export default function RisksPage() {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchRisks();
  }, [filter]);

  const fetchRisks = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await getRisks(params);
      setRisks(data.risks || []);
    } catch (error) {
      console.error('Error fetching risks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessRisk = async (riskId: string) => {
    setProcessing(riskId);
    try {
      await processRisk(riskId);
      await fetchRisks(); // Refresh
    } catch (error) {
      console.error('Error processing risk:', error);
      alert('Error processing risk');
    } finally {
      setProcessing(null);
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
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Revenue Risks</h1>
          <p className="text-gray-600 mt-2">Monitor and manage revenue at risk</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex space-x-2">
        {['all', 'active', 'recovered', 'lost'].map((status) => (
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

      {/* Risks Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {risks.map((risk) => (
              <tr key={risk.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="w-5 h-5 text-orange-500 mt-0.5" />
                    <div>
                      <Link
                        href={`/risks/${risk.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700"
                      >
                        {risk.risk_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Link>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatRelativeTime(risk.detected_at)}
                      </p>
                      {risk.has_ai_diagnosis && (
                        <span className="inline-flex items-center mt-1 text-xs text-green-600">
                          <span className="mr-1">✓</span> AI Analyzed
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{risk.customer_email}</div>
                  <div className="text-xs text-gray-500">{risk.customer_id}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm font-semibold text-gray-900">
                    {formatCurrency(risk.risk_amount)}
                  </div>
                  {risk.risk_score && (
                    <div className="text-xs text-gray-500">Score: {risk.risk_score}%</div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col space-y-1">
                    <Badge variant="status" value={risk.status}>
                      {risk.status}
                    </Badge>
                    <Badge variant="priority" value={risk.priority}>
                      {risk.priority}
                    </Badge>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {risk.status === 'active' && !risk.has_ai_diagnosis && (
                    <button
                      onClick={() => handleProcessRisk(risk.id)}
                      disabled={processing === risk.id}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none disabled:opacity-50"
                    >
                      {processing === risk.id ? (
                        <>
                          <Loader2 className="animate-spin -ml-0.5 mr-1 h-3 w-3" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Play className="-ml-0.5 mr-1 h-3 w-3" />
                          Process with AI
                        </>
                      )}
                    </button>
                  )}
                  <Link
                    href={`/risks/${risk.id}`}
                    className="ml-2 inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {risks.length === 0 && (
          <div className="text-center py-12">
            <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No risks found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'all' ? 'No risks detected yet' : `No ${filter} risks`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
