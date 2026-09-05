'use client';

import { AlertTriangle } from 'lucide-react';

export default function AuditPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
        <p className="text-gray-600 mt-2">Complete compliance and decision history</p>
      </div>

      <div className="bg-white rounded-lg shadow border border-gray-200 p-12 text-center">
        <AlertTriangle className="mx-auto h-16 w-16 text-gray-400 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Audit Trail Coming Soon</h2>
        <p className="text-gray-600 mb-4">
          This feature will show complete audit logs of all AI decisions, interventions, and compliance checks.
        </p>
        <div className="mt-8 text-left max-w-2xl mx-auto bg-gray-50 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Planned Features:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Complete decision history with AI reasoning
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Compliance check results and timestamps
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              User actions and system events
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Exportable audit reports for regulatory compliance
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
