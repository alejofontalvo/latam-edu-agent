import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000"
});

export const getHealth = () => api.get("/health").then((r) => r.data);
export const getDatasets = () => api.get("/datasets").then((r) => r.data);
export const getDataset = (id) => api.get(`/datasets/${id}`).then((r) => r.data);
export const getDatasetSummary = (id) => api.get(`/datasets/${id}/summary`).then((r) => r.data);
export const getDatasetFilters = (id) => api.get(`/datasets/${id}/filters`).then((r) => r.data);
export const getCountries = () => api.get("/countries").then((r) => r.data);
export const getExams = () => api.get("/exams").then((r) => r.data);
export const getKpis = () => api.get("/analytics/kpis").then((r) => r.data);
export const getBasicAnalytics = (id) => api.get(`/analytics/basic/${id}`).then((r) => r.data);
export const queryAnalytics = (payload) => api.post("/analytics/query", payload).then((r) => r.data);
export const compareAnalytics = (payload) => api.post("/analytics/compare", payload).then((r) => r.data);
export const autoAnalytics = (payload) => api.post("/analytics/auto", payload).then((r) => r.data);
export const overviewAnalytics = (payload = {}) => api.post("/analytics/overview", payload).then((r) => r.data);
export const sendChat = (payload) => api.post("/chat", payload).then((r) => r.data);
export const generateEvaluation = (payload) => api.post("/evaluations/generate", payload).then((r) => r.data);
export const getDocuments = () => api.get("/rag/documents").then((r) => r.data);
export const queryRag = (payload) => api.post("/rag/query", payload).then((r) => r.data);
export const exportCsv = (id) => api.get(`/reports/export/csv/${id}`).then((r) => r.data);
export const exportExcel = (id) => api.get(`/reports/export/excel/${id}`).then((r) => r.data);
export const getPowerBiDataset = (id) => api.get(`/powerbi/dataset/${id}`).then((r) => r.data);
export const getPowerBiCatalog = () => api.get("/powerbi/catalog").then((r) => r.data);
export const getPowerBiKpis = () => api.get("/powerbi/kpis").then((r) => r.data);
export const getPowerBiComparisons = () => api.get("/powerbi/comparisons").then((r) => r.data);

export default api;
