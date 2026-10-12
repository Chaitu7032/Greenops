import {
  DashboardOverview,
  Repository,
  RepositoryRanking,
  Sprint,
  BurnDownPoint,
  CarbonTimeSeriesPoint,
  CostTimeSeriesPoint,
  SavingsAnalysis,
  PipelineRun,
  Policy,
  DeferredJob,
} from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    // Prevent stale caching in development / telemetry dashboards
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "");
    throw new Error(
      `API Error [${res.status} ${res.statusText}] at ${endpoint}: ${errorText}`
    );
  }

  return res.json();
}

export const api = {
  // Health & Readiness
  getHealth: () => request<{ status: string }>("/healthz"),
  getReadiness: () =>
    request<{
      status: string;
      database: boolean;
      redis: boolean;
      environment: string;
      errors?: string[] | null;
    }>("/ready"),

  // Dashboard Analytics
  getDashboardOverview: () =>
    request<DashboardOverview>("/api/v1/dashboard/overview"),
  getRepositoryRankings: () =>
    request<RepositoryRanking[]>("/api/v1/dashboard/repositories"),
  getCostAnalytics: () =>
    request<CostTimeSeriesPoint[]>("/api/v1/dashboard/cost"),
  getCarbonAnalytics: () =>
    request<CarbonTimeSeriesPoint[]>("/api/v1/dashboard/carbon"),
  getSavingsAnalysis: () =>
    request<SavingsAnalysis>("/api/v1/dashboard/savings"),

  // Repositories
  getRepositories: () => request<Repository[]>("/api/v1/repositories"),
  getRepository: (id: string) =>
    request<Repository>(`/api/v1/repositories/${id}`),
  getRepositoryPipelines: (id: string, limit = 50) =>
    request<PipelineRun[]>(`/api/v1/repositories/${id}/pipelines?limit=${limit}`),

  // Pipelines
  getPipelines: (params?: {
    repository_id?: string;
    sprint_id?: string;
    policy_decision?: string;
    execution_status?: string;
    limit?: number;
    offset?: number;
  }) => {
    const query = new URLSearchParams();
    if (params?.repository_id) query.set("repository_id", params.repository_id);
    if (params?.sprint_id) query.set("sprint_id", params.sprint_id);
    if (params?.policy_decision) query.set("policy_decision", params.policy_decision);
    if (params?.execution_status) query.set("execution_status", params.execution_status);
    if (params?.limit) query.set("limit", params.limit.toString());
    if (params?.offset) query.set("offset", params.offset.toString());
    const qs = query.toString();
    return request<PipelineRun[]>(`/api/v1/pipelines${qs ? `?${qs}` : ""}`);
  },
  getPipelineRun: (id: string) =>
    request<PipelineRun>(`/api/v1/pipelines/${id}`),

  // Sprints
  getSprints: () => request<Sprint[]>("/api/v1/sprints"),
  getSprint: (id: string) => request<Sprint>(`/api/v1/sprints/${id}`),
  getSprintBudget: (id: string) =>
    request<any>(`/api/v1/sprints/${id}/budget`),
  getSprintBurnDown: (id: string) =>
    request<BurnDownPoint[]>(`/api/v1/sprints/${id}/burn-down`),

  // Policies
  getPolicies: () => request<Policy[]>("/api/v1/policies"),
  getPolicy: (id: string) => request<Policy>(`/api/v1/policies/${id}`),
  createPolicy: (data: Partial<Policy>) =>
    request<Policy>("/api/v1/policies", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updatePolicy: (id: string, data: Partial<Policy>) =>
    request<Policy>(`/api/v1/policies/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Deferred Jobs
  getDeferredJobs: (statusFilter?: string) => {
    const qs = statusFilter ? `?status_filter=${statusFilter}` : "";
    return request<DeferredJob[]>(`/api/v1/deferred-jobs${qs}`);
  },
  getDeferredJob: (id: string) =>
    request<DeferredJob>(`/api/v1/deferred-jobs/${id}`),
  dispatchDeferredJob: (id: string) =>
    request<DeferredJob>(`/api/v1/deferred-jobs/${id}/dispatch`, {
      method: "POST",
    }),

  // Demo Seeding
  seedDemoData: () =>
    request<{ status: string; message: string }>("/api/v1/demo/seed", {
      method: "POST",
    }),
};
