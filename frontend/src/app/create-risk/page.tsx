'use client';

import { useState } from 'react';
import { Code, Plus, AlertCircle, CheckCircle } from 'lucide-react';

export default function CreateRiskPage() {
  const [activeTab, setActiveTab] = useState<'api' | 'manual'>('api');
  const [formData, setFormData] = useState({
    customer_email: '',
    customer_name: '',
    amount: '',
    risk_type: 'payment_failure',
    failure_reason: '',
    priority: 'medium'
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/risks/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_email: formData.customer_email,
          customer_name: formData.customer_name,
          amount: parseFloat(formData.amount),
          risk_type: formData.risk_type,
          failure_reason: formData.failure_reason,
          priority: formData.priority
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create risk');
      }

      const data = await response.json();
      setResult({ type: 'success', message: `Risk created successfully! ID: ${data.risk_id}` });

      // Reset form
      setFormData({
        customer_email: '',
        customer_name: '',
        amount: '',
        risk_type: 'payment_failure',
        failure_reason: '',
        priority: 'medium'
      });
    } catch (error: any) {
      setResult({ type: 'error', message: error.message });
    } finally {
      setSubmitting(false);
    }
  };

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://your-backend.onrender.com';

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Risk</h1>
        <p className="text-gray-600 mt-2">Import risks via API or add manually for demo</p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveTab('api')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'api'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Code className="inline w-4 h-4 mr-2" />
            API Integration (Production)
          </button>
          <button
            onClick={() => setActiveTab('manual')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'manual'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Plus className="inline w-4 h-4 mr-2" />
            Manual Entry (Demo Only)
          </button>
        </div>
      </div>

      {/* API Tab */}
      {activeTab === 'api' && (
        <div className="space-y-6">
          {/* Info Banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
              <div>
                <h3 className="font-semibold text-blue-900">Production Integration</h3>
                <p className="text-sm text-blue-700 mt-1">
                  In production, connect this API to your payment gateway, e-commerce platform, or billing system
                  to automatically detect and import revenue risks in real-time.
                </p>
              </div>
            </div>
          </div>

          {/* API Documentation */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">API Endpoint</h2>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Endpoint URL:</p>
              <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
                POST {apiUrl}/api/v1/risks/create
              </div>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Headers:</p>
              <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
                Content-Type: application/json
              </div>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Request Body:</p>
              <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm overflow-x-auto">
                {`{
  "customer_email": "customer@example.com",
  "customer_name": "Rajesh Kumar",
  "amount": 15000,
  "risk_type": "payment_failure",
  "failure_reason": "Card expired",
  "priority": "high",
  "transaction_id": "TXN12345",  // optional
  "payment_method": "card"       // optional
}`}
              </div>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Risk Types:</p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="bg-gray-50 p-2 rounded"><code>payment_failure</code> - Failed transactions</div>
                <div className="bg-gray-50 p-2 rounded"><code>checkout_abandonment</code> - Cart abandoned</div>
                <div className="bg-gray-50 p-2 rounded"><code>subscription_failure</code> - Renewal failed</div>
                <div className="bg-gray-50 p-2 rounded"><code>b2b_receivable</code> - Invoice overdue</div>
              </div>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Example with cURL:</p>
              <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-xs overflow-x-auto">
                {`curl -X POST ${apiUrl}/api/v1/risks/create \\
  -H "Content-Type: application/json" \\
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "Rajesh Kumar",
    "amount": 15000,
    "risk_type": "payment_failure",
    "failure_reason": "Card expired",
    "priority": "high"
  }'`}
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Response (Success):</p>
              <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
                {`{
  "risk_id": "uuid-here",
  "status": "created",
  "message": "Risk created successfully"
}`}
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Use Cases</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Payment Gateway Webhook</p>
                  <p className="text-gray-600">Connect Razorpay/Stripe webhooks to auto-import failed payments</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">E-commerce Platform</p>
                  <p className="text-gray-600">Import abandoned carts from Shopify/WooCommerce</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Subscription Billing</p>
                  <p className="text-gray-600">Auto-detect failed renewals from Chargebee/Stripe Billing</p>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">B2B Invoicing</p>
                  <p className="text-gray-600">Import overdue invoices from accounting systems</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manual Tab */}
      {activeTab === 'manual' && (
        <div className="space-y-6">
          {/* Warning Banner */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
              <div>
                <h3 className="font-semibold text-yellow-900">Demo Purpose Only</h3>
                <p className="text-sm text-yellow-700 mt-1">
                  This manual form is for demonstration purposes. In production, risks should be automatically imported
                  via the API endpoint from your payment systems.
                </p>
              </div>
            </div>
          </div>

          {/* Manual Form */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Add Risk Manually</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.customer_email}
                    onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="customer@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer Name
                  </label>
                  <input
                    type="text"
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Rajesh Kumar"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount (₹) *
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="15000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Risk Type *
                  </label>
                  <select
                    required
                    value={formData.risk_type}
                    onChange={(e) => setFormData({ ...formData, risk_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="payment_failure">Payment Failure</option>
                    <option value="checkout_abandonment">Checkout Abandonment</option>
                    <option value="subscription_failure">Subscription Failure</option>
                    <option value="b2b_receivable">B2B Receivable</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Failure Reason
                  </label>
                  <input
                    type="text"
                    value={formData.failure_reason}
                    onChange={(e) => setFormData({ ...formData, failure_reason: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Card expired"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority *
                  </label>
                  <select
                    required
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>

              {result && (
                <div className={`p-4 rounded-lg ${
                  result.type === 'success' ? 'bg-green-50 text-green-900' : 'bg-red-50 text-red-900'
                }`}>
                  <div className="flex items-center">
                    {result.type === 'success' ? (
                      <CheckCircle className="w-5 h-5 mr-2" />
                    ) : (
                      <AlertCircle className="w-5 h-5 mr-2" />
                    )}
                    <p className="text-sm font-medium">{result.message}</p>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setFormData({
                    customer_email: '',
                    customer_name: '',
                    amount: '',
                    risk_type: 'payment_failure',
                    failure_reason: '',
                    priority: 'medium'
                  })}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Reset
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Creating...' : 'Create Risk'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
