export interface Organization {
  id: string;
  name: string;
  monthly_budget_usd: number | string;
  carbon_budget_kg: number | string;
  active_sprint_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Repository {
  id: string;
  organization_id: string;
  github_repo_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
  runner_type: string;
  runner_region: string;
  cpu_cores: number;
  memory_gb: number | string;
  cost_per_minute: number | string;
  power_idle_watts: number | string;
  power_max_watts: number | string;
  pue: number | string;
  created_at: string;
}

export interface Sprint {
  id: string;
  organization_id: string;
  name: string;
  external_sprint_id?: string | null;
  start_date: string;
  end_date: string;
  budget_usd: number | string;
  carbon_budget_kg: number | string;
  status: string;
  created_at: string;
}

export interface PipelineRun {
  id: string;
  repository_id: string;
  organization_id: string;
  sprint_id?: string | null;
  pr_number?: number | null;
  commit_sha: string;
  author: string;
  workflow_name: string;
  trigger_type: string;
  changed_files_count: number;
  lines_added: number;
  lines_deleted: number;
  source_files_count: number;
  test_files_count: number;
  documentation_files_count: number;
  configuration_files_count: number;
  integration_files_count: number;
  estimated_duration_seconds?: number | string | null;
  actual_duration_seconds?: number | string | null;
  estimated_cost_usd?: number | string | null;
  actual_cost_usd?: number | string | null;
  estimated_energy_kwh?: number | string | null;
  actual_energy_kwh?: number | string | null;
  grid_region: string;
  grid_intensity_gco2_kwh: number | string;
  estimated_carbon_g?: number | string | null;
  actual_carbon_g?: number | string | null;
  urgency: string;
  policy_decision: "APPROVED" | "DEFERRED" | "FLAGGED";
  policy_reason?: string | null;
  execution_status: string;
  created_at: string;
  repository_name?: string | null;
  duration_variance_seconds?: number | string | null;
  cost_variance_usd?: number | string | null;
  carbon_variance_g?: number | string | null;
}

export interface Policy {
  id: string;
  organization_id?: string | null;
  repository_id?: string | null;
  name: string;
  max_cost_per_run_usd: number | string;
  max_carbon_per_run_g: number | string;
  budget_warning_percent: number | string;
  budget_block_percent: number | string;
  high_grid_intensity_threshold: number | string;
  allow_deferred_execution: boolean;
  created_at: string;
}

export interface DeferredJob {
  id: string;
  pipeline_run_id: string;
  repository_id: string;
  repository_name?: string | null;
  pr_number: number;
  workflow_name: string;
  target_ref: string;
  scheduled_for: string;
  reason: string;
  priority: string;
  status: string;
  attempts: number;
  last_error?: string | null;
  created_at: string;
}

export interface DashboardOverview {
  financial_budget_usd: number | string;
  financial_consumed_usd: number | string;
  financial_remaining_usd: number | string;
  financial_percentage: number;
  financial_over_budget: boolean;
  carbon_budget_kg: number | string;
  carbon_consumed_kg: number | string;
  carbon_remaining_kg: number | string;
  carbon_percentage: number;
  carbon_over_budget: boolean;
  total_runs_count: number;
  approved_runs_count: number;
  deferred_runs_count: number;
  flagged_runs_count: number;
  estimated_savings_usd: number | string;
  carbon_avoided_kg: number | string;
  grid_region: string;
  current_grid_intensity: number | string;
  is_grid_data_stale: boolean;
  is_demo_data?: boolean;
}

export interface RepositoryRanking {
  id: string;
  name: string;
  owner: string;
  full_name: string;
  total_runs: number;
  total_cost_usd: number | string;
  total_carbon_kg: number | string;
  deferred_count: number;
  avg_duration_minutes: number;
}

export interface BurnDownPoint {
  date: string;
  budget_remaining_usd: number;
  actual_spent_usd: number;
  ideal_burn_usd: number;
}

export interface CostTimeSeriesPoint {
  date: string;
  cost_usd: number;
  budget_limit_usd: number;
}

export interface CarbonTimeSeriesPoint {
  date: string;
  emissions_kg: number;
  grid_intensity_gco2: number;
}

export interface SavingsAnalysis {
  total_savings_usd: number | string;
  total_carbon_avoided_kg: number | string;
  deferred_jobs_executed: number;
  green_window_efficiency_pct: number;
  prevented_unnecessary_runs: number;
}
