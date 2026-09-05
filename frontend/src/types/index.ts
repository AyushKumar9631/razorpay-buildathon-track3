export interface AnalyticsOverview {
  total_revenue_at_risk: number;
  total_revenue_recovered: number;
  recovery_rate: number;
  active_risks: number;
  active_interventions: number;
  avg_recovery_time_hours: number;
  by_priority?: Record<string, number>;
  by_type?: Record<string, {
    count: number;
    amount: number;
  }>;
  last_24h: {
    new_risks: number;
    recovered: number;
  };
}

export interface Risk {
  id: string;
  risk_type: string;
  risk_amount: number;
  risk_score: number | null;
  status: string;
  priority: string;
  detected_at: string;
  customer_id: string;
  customer_email: string;
  root_cause: string | null;
  has_ai_diagnosis?: boolean;
  ai_diagnosis?: any;
}

export interface RiskDetail extends Risk {
  customer: {
    id: string;
    email: string;
    name: string;
    tier: string;
  };
  interventions: Intervention[];
}

export interface Intervention {
  id: string;
  risk_id?: string;
  revenue_risk_id?: string;
  intervention_type: string;
  intervention_strategy?: string;
  strategy?: string;
  channel: string;
  status: string;
  outcome: string | null;
  scheduled_at: string | null;
  executed_at: string | null;
  ai_reasoning?: string;
}

export interface RecoveryTimeline {
  date: string;
  daily_amount: number;
  cumulative_amount: number;
  recoveries: number;
}

export interface InterventionEffectiveness {
  by_type: Record<string, {
    total: number;
    successful: number;
    success_rate: number;
  }>;
  by_channel: Record<string, {
    total: number;
    successful: number;
    success_rate: number;
  }>;
}
