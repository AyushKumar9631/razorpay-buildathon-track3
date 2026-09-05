'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, AlertTriangle, Loader2, User, Calendar, DollarSign, TrendingUp } from 'lucide-react';
import Badge from '@/components/Badge';
import { formatCurrency, formatDate } from '@/lib/utils';

interface RiskDetail {
  id: string;
  risk_type: string;
  risk_amount: number;
  risk_score: number | null;
  status: string;
  priority: string;
  detected_at: string;
  root_cause: string | null;
  ai_diagnosis: any;
  customer: {
    customer_id: string;
    email: string;
    name: string;
    tier: string;
  };
}

export default function RiskDetailPage() {
  const params = useParams();
  const riskId = params.id as string;
  const [risk, setRisk] = useState<RiskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRiskDetail();
  }, [riskId]);

  const fetchRiskDetail = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/risks/${riskId}`);

      if (!response.ok) {
        throw new Error('Risk not found');
      }

      const data = await response.json();
      setRisk(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessWithAI = async () => {
    if (!risk || processing) return;

    setProcessing(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/risks/${riskId}/process`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to process risk');
      }

      // Refresh risk data
      await fetchRiskDetail();
      alert('Risk processed successfully with AI!');
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const handleMarkRecovered = async () => {
    if (!risk) return;

    const confirmed = confirm('Mark this risk as recovered?');
    if (!confirmed) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/risks/${riskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'recovered' }),
      });

      if (!response.ok) {
        throw new Error('Failed to update risk');
      }

      await fetchRiskDetail();
      alert('Risk marked as recovered!');
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const hasAIAnalysis = risk?.ai_diagnosis && Object.keys(risk.ai_diagnosis).length > 0;

  if (loading) {
    return (
      <div className="p-8">
        <div className="mb-8 text-center">
          <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 text-sm">Loading risk details...</p>
          <p className="text-gray-500 text-xs mt-2">⏳ Render free tier may take 30-60 seconds on first load. Please be patient.</p>
        </div>

        {/* Skeleton Loading */}
        <div className="mb-6">
          <div className="h-10 w-32 bg-gray-200 rounded animate-pulse"></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="space-y-3">
                <div className="h-4 bg-gray-100 rounded w-full"></div>
                <div className="h-4 bg-gray-100 rounded w-3/4"></div>
                <div className="h-4 bg-gray-100 rounded w-5/6"></div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-32 bg-gray-100 rounded"></div>
            </div>
          </div>
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="space-y-3">
                <div className="h-4 bg-gray-100 rounded"></div>
                <div className="h-4 bg-gray-100 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !risk) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-red-900 mb-2">Risk Not Found</h2>
          <p className="text-red-700 mb-4">{error || 'The requested risk could not be found.'}</p>
          <Link
            href="/risks"
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Risks
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/risks"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Risks
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Risk Details</h1>
            <p className="text-gray-600 mt-1">
              {risk.risk_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="status" value={risk.status}>
              {risk.status}
            </Badge>
            <Badge variant="priority" value={risk.priority}>
              {risk.priority}
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Risk Summary */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Summary</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Amount at Risk</p>
                <p className="text-2xl font-bold text-orange-600">
                  {formatCurrency(risk.risk_amount)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Risk Score</p>
                <p className="text-2xl font-bold text-red-600">
                  {risk.risk_score ? `${risk.risk_score}%` : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Detected</p>
                <p className="text-sm font-medium text-gray-900">
                  {formatDate(risk.detected_at)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {risk.status}
                </p>
              </div>
            </div>
          </div>

          {/* AI Diagnosis */}
          {risk.ai_diagnosis && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Analysis</h2>
              <div className="space-y-4">
                {risk.ai_diagnosis.diagnosis && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Diagnosis</p>
                    <p className="text-sm text-gray-900 bg-blue-50 p-3 rounded">
                      {risk.ai_diagnosis.diagnosis}
                    </p>
                  </div>
                )}
                {risk.ai_diagnosis.recommended_intervention && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Recommended Action</p>
                    <p className="text-sm text-gray-900 bg-green-50 p-3 rounded">
                      {risk.ai_diagnosis.recommended_intervention}
                    </p>
                  </div>
                )}
                {risk.ai_diagnosis.reasoning && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">AI Reasoning</p>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                      {risk.ai_diagnosis.reasoning}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Root Cause */}
          {risk.root_cause && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Root Cause</h2>
              <p className="text-sm text-gray-700">{risk.root_cause}</p>
            </div>
          )}

          {!risk.ai_diagnosis && !risk.root_cause && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6 text-center">
              <AlertTriangle className="mx-auto h-12 w-12 text-gray-400 mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No AI Analysis Yet</h3>
              <p className="text-sm text-gray-600 mb-4">
                This risk hasn't been processed by AI yet. Click the button below to analyze.
              </p>
              <button
                onClick={handleProcessWithAI}
                disabled={processing}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Processing...' : 'Process with AI'}
              </button>
            </div>
          )}
        </div>

        {/* Right Column - Customer Info */}
        <div className="space-y-6">
          {/* Customer Details */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="w-5 h-5 mr-2" />
              Customer
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-600">Customer ID</p>
                <p className="text-sm font-medium text-gray-900">{risk.customer.customer_id}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Email</p>
                <p className="text-sm font-medium text-gray-900">{risk.customer.email}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Name</p>
                <p className="text-sm font-medium text-gray-900">{risk.customer.name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Tier</p>
                <Badge variant="priority" value={risk.customer.tier}>
                  {risk.customer.tier}
                </Badge>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <button
                onClick={handleProcessWithAI}
                disabled={processing || hasAIAnalysis}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Processing...' : hasAIAnalysis ? 'Already Analyzed' : 'Process with AI'}
              </button>
              <button
                onClick={handleMarkRecovered}
                disabled={risk.status === 'recovered'}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {risk.status === 'recovered' ? 'Already Recovered' : 'Mark as Recovered'}
              </button>
              <Link
                href={`/interventions?risk_id=${riskId}`}
                className="block w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm text-center"
              >
                View Interventions
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
