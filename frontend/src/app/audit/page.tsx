'use client';

import { useEffect, useState } from 'react';
import { formatDate } from '@/lib/utils';
import { FileText, User, Zap, DollarSign, AlertTriangle, CheckCircle, Shield } from 'lucide-react';
import Badge from '@/components/Badge';

interface AuditEntry {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  details: any;
  compliance_check: any;
  timestamp: string;
}

export default function AuditPage() {
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/audit/logs?limit=100`);

      if (response.ok) {
        const data = await response.json();
        setAuditLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (entityType: string) => {
    switch (entityType) {
      case 'revenue_risk':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case 'intervention':
        return <Zap className="w-5 h-5 text-purple-500" />;
      case 'recovery_outcome':
        return <DollarSign className="w-5 h-5 text-green-500" />;
      case 'customer':
        return <User className="w-5 h-5 text-blue-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getActionColor = (action: string) => {
    if (action.includes('detected') || action.includes('created')) return 'orange';
    if (action.includes('completed') || action.includes('recovered')) return 'green';
    if (action.includes('executed')) return 'purple';
    if (action.includes('failed')) return 'red';
    return 'blue';
  };

  const filteredLogs = filter === 'all'
    ? auditLogs
    : auditLogs.filter(log => log.entity_type === filter);

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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Shield className="w-8 h-8 mr-3 text-blue-600" />
              Audit Trail
            </h1>
            <p className="text-gray-600 mt-2">Complete compliance and decision history</p>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-gray-900">
              {auditLogs.length} Total Entries
            </span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex space-x-2">
        {['all', 'revenue_risk', 'intervention', 'recovery_outcome', 'customer'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === type
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {type === 'all' ? 'All Entries' : type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Risk Detections</p>
              <p className="text-2xl font-bold text-orange-600">
                {auditLogs.filter(l => l.action.includes('risk_detected')).length}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-500 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">AI Analyses</p>
              <p className="text-2xl font-bold text-blue-600">
                {auditLogs.filter(l => l.action.includes('ai_analysis')).length}
              </p>
            </div>
            <FileText className="w-8 h-8 text-blue-500 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Interventions</p>
              <p className="text-2xl font-bold text-purple-600">
                {auditLogs.filter(l => l.action.includes('intervention')).length}
              </p>
            </div>
            <Zap className="w-8 h-8 text-purple-500 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Recoveries</p>
              <p className="text-2xl font-bold text-green-600">
                {auditLogs.filter(l => l.action.includes('recovered')).length}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-500 opacity-50" />
          </div>
        </div>
      </div>

      {/* Audit Log Timeline */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Activity Timeline</h2>
        </div>
        <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
          {filteredLogs.length > 0 ? (
            filteredLogs.map((log) => (
              <div key={log.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    {getIcon(log.entity_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Badge variant="status" value={getActionColor(log.action)}>
                          {log.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Badge>
                        <span className="text-xs text-gray-500">by</span>
                        <Badge variant="priority" value={log.actor === 'ai_agent' ? 'high' : 'medium'}>
                          {log.actor}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(log.timestamp)}
                      </span>
                    </div>

                    {/* Details */}
                    {log.details && (
                      <div className="mt-2 bg-gray-50 rounded p-3">
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {Object.entries(log.details).slice(0, 4).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-gray-600 font-medium">
                                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                              </span>
                              <span className="ml-1 text-gray-900">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Compliance Check */}
                    {log.compliance_check && (
                      <div className="mt-2 flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="text-xs text-green-700 font-medium">
                          Compliance: {log.compliance_check.passed ? 'Passed' : 'Failed'}
                        </span>
                        {log.compliance_check.checks && (
                          <span className="text-xs text-gray-600">
                            ({log.compliance_check.checks.join(', ')})
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400 mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Audit Logs Found</h3>
              <p className="text-sm text-gray-600">
                {filter === 'all'
                  ? 'No audit trail entries have been created yet.'
                  : `No ${filter.replace(/_/g, ' ')} entries found.`}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
