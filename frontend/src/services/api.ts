import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface AnalysisReport {
  dataset_id: string;
  report_id?: string;
  problem_type: string;
  problem_description: string;
  quality_scores: {
    completeness: number;
    consistency: number;
    validity: number;
    overall: number;
  };
  shape: {
    rows: number;
    columns: number;
  };
  dtypes?: Record<string, string>;
  missing_values?: {
    columns: string[];
    counts: Record<string, number>;
    percentages: Record<string, number>;
  };
  outliers?: {
    columns: string[];
    counts: Record<string, number>;
    percentages: Record<string, number>;
  };
  class_imbalance?: {
    columns: string[];
    distributions: Record<string, Record<string, number>>;
    imbalance_ratios: Record<string, number>;
  };
  pii_report: {
    summary: {
      columns_with_pii: number;
      total_pii_values?: number;
    };
    details?: Record<string, any>;
  };
  recommendations: Array<{
    category: string;
    severity: string;
    suggestion: string;
    code_example?: string;
  }>;
  priority_actions: string[];
  overall_assessment: string;
  domain_resources?: Array<{
    title: string;
    url: string;
    summary: string;
    type: string;
    relevance_score?: number;
  }>;
  resources_status?: "pending" | "loading" | "complete" | "error";
  created_at?: string;
}

export const senalignAPI = {
  /**
   * Upload a dataset file with problem description
   */
  uploadDataset: async (file: File, problemDescription: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("problem_description", problemDescription);

    const response = await api.post("/api/v1/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Analyze a dataset by ID
   */
  analyzeDataset: async (
    datasetId: string,
    userEmail: string = "user@senalign.com",
  ): Promise<AnalysisReport> => {
    const response = await api.post(`/api/v1/analyze/${datasetId}`, null, {
      headers: {
        "user-email": userEmail,
      },
    });
    return response.data;
  },

  /**
   * Fetch domain resources for a dataset (async)
   */
  fetchResources: async (datasetId: string) => {
    const response = await api.post(`/api/v1/analyze/${datasetId}/resources`);
    return response.data;
  },

  /**
   * Get resources status for a report (for polling)
   */
  getReportResources: async (reportId: string) => {
    const response = await api.get(`/api/v1/reports/${reportId}/resources`);
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    const response = await api.get("/health");
    return response.data;
  },

  // ============ Payment API Methods ============

  /**
   * Get token pricing information
   */
  getPricing: async () => {
    const response = await api.get("/api/v1/payment/pricing");
    return response.data;
  },

  /**
   * Purchase tokens
   */
  purchaseTokens: async (tokenAmount: number, userEmail: string) => {
    const response = await api.post("/api/v1/payment/purchase", {
      token_amount: tokenAmount,
      user_email: userEmail,
      currency: "NGN",
    });
    return response.data;
  },

  /**
   * Verify payment transaction
   */
  verifyPayment: async (transactionReference: string) => {
    const response = await api.post(
      `/api/v1/payment/verify/${transactionReference}`,
    );
    return response.data;
  },

  /**
   * Get user token balance
   */
  getTokenBalance: async (userEmail: string) => {
    const response = await api.get(`/api/v1/payment/balance/${userEmail}`);
    return response.data;
  },

  /**
   * Get token consumption history
   */
  getConsumptionHistory: async (userEmail: string, limit: number = 50) => {
    const response = await api.get(
      `/api/v1/payment/balance/${userEmail}/history?limit=${limit}`,
    );
    return response.data;
  },

  /**
   * Get transaction status
   */
  getTransactionStatus: async (transactionReference: string) => {
    const response = await api.get(
      `/api/v1/payment/transaction/${transactionReference}`,
    );
    return response.data;
  },

  /**
   * Get inline checkout configuration
   */
  getInlineCheckoutConfig: async (amount: number, userEmail: string) => {
    const response = await api.get(
      `/api/v1/payment/inline-config?amount=${amount}&user_email=${userEmail}`,
    );
    return response.data;
  },
};

export default api;
