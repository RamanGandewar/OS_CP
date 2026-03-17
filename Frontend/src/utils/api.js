import axios from "axios";

const client = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
  withCredentials: true,
});

const listQuery = (q, extra = {}) => ({
  params: {
    ...(q ? { q } : {}),
    ...extra,
  },
});

export const authApi = {
  login: (payload) => client.post("/auth/login", payload),
  logout: () => client.post("/auth/logout"),
  me: () => client.get("/auth/me"),
};

export const usersApi = {
  list: () => client.get("/users"),
};

export const customersApi = {
  list: (q = "") => client.get("/customers", listQuery(q)),
  create: (payload) => client.post("/customers", payload),
  exportList: () => client.post("/customers/export"),
};

export const enquiriesApi = {
  list: (q = "", status = "") => client.get("/enquiries", listQuery(q, status ? { status } : {})),
  create: (payload) => client.post("/enquiries", payload),
};

export const quotationsApi = {
  list: (q = "") => client.get("/quotations", listQuery(q)),
  create: (payload) => client.post("/quotations", payload),
};

export const ordersApi = {
  list: (q = "") => client.get("/sales-orders", listQuery(q)),
  create: (payload) => client.post("/sales-orders", payload),
};

export const invoicesApi = {
  list: (q = "") => client.get("/invoices", listQuery(q)),
  create: (payload) => client.post("/invoices", payload),
};

export const reportsApi = {
  summary: () => client.get("/reports/summary"),
  counts: () => client.get("/reports/counts"),
  generate: (payload) => client.post("/reports/generate", payload),
};

export const processApi = {
  monitor: () => client.get("/processes/monitor"),
  logs: (limit = 100) => client.get("/processes/logs", { params: { limit } }),
  createBackgroundTask: (payload) => client.post("/processes/background-task", payload),
};

export const schedulerApi = {
  tasks: () => client.get("/scheduler/tasks"),
  addTask: (payload) => client.post("/scheduler/tasks", payload),
  run: (payload) => client.post("/scheduler/run", payload),
  compare: () => client.get("/scheduler/compare"),
  reset: () => client.post("/scheduler/reset"),
  ganttUrl: (algorithm) => `http://127.0.0.1:5000/api/scheduler/gantt/${algorithm.toLowerCase()}`,
};

export const threadApi = {
  monitor: () => client.get("/threads/monitor"),
  startAutoSave: (payload) => client.post("/threads/auto-save", payload),
  reportJob: (payload) => client.post("/threads/report-job", payload),
  validationJob: (payload) => client.post("/threads/validation-job", payload),
  syncJob: (payload) => client.post("/threads/sync-job", payload),
  stop: (threadName) => client.post(`/threads/stop/${threadName}`),
};

export const syncApi = {
  monitor: () => client.get("/sync/monitor"),
  quotationEdit: (payload) => client.post("/sync/quotation-edit", payload),
  reserveInventory: (payload) => client.post("/sync/inventory/reserve", payload),
  readReport: (payload) => client.post("/sync/report/read", payload),
  writeReport: (payload) => client.post("/sync/report/write", payload),
  produce: (payload) => client.post("/sync/producer", payload),
  consume: () => client.post("/sync/consumer"),
  raceDemo: () => client.get("/sync/race-demo"),
};

export const deadlockApi = {
  initResources: () => client.post("/deadlock/init-resources"),
  state: () => client.get("/deadlock/state"),
  createScenario: () => client.post("/deadlock/scenario/create"),
  detect: () => client.get("/deadlock/detect"),
  bankerCheck: (payload) => client.post("/deadlock/banker-check", payload),
  recover: (payload) => client.post("/deadlock/recover", payload),
  reset: () => client.post("/deadlock/reset"),
  events: () => client.get("/deadlock/events"),
  graphUrl: (stamp) => `http://127.0.0.1:5000/api/deadlock/graph?ts=${stamp}`,
};

export const memoryApi = {
  monitor: () => client.get("/memory/monitor"),
  loadPage: (payload) => client.post("/memory/report/page", payload),
  customerCache: (payload) => client.post("/memory/cache/customer", payload),
  quotationCache: (payload) => client.post("/memory/cache/quotation", payload),
  userPreferenceCache: (payload) => client.post("/memory/cache/user-preference", payload),
  compareReplacement: (payload) => client.post("/memory/replacement/compare", payload),
  allocate: (payload) => client.post("/memory/allocator/allocate", payload),
  reset: () => client.post("/memory/reset"),
  chartUrl: (chartName, stamp) => `http://127.0.0.1:5000/api/memory/charts/${chartName}?ts=${stamp}`,
};

export const ioApi = {
  monitor: () => client.get("/io/monitor"),
  addRequest: (payload) => client.post("/io/requests", payload),
  compare: (payload) => client.post("/io/compare", payload),
  allocateBuffer: (payload) => client.post("/io/buffer/allocate", payload),
  releaseBuffer: (payload) => client.post("/io/buffer/release", payload),
  enqueuePrint: (payload) => client.post("/io/spool/enqueue", payload),
  processPrint: () => client.post("/io/spool/process"),
  chartUrl: (chartName, stamp) => `http://127.0.0.1:5000/api/io/charts/${chartName}?ts=${stamp}`,
};

export const dashboardApi = {
  snapshot: () => client.get("/dashboard/snapshot"),
  generateAnalytics: () => client.post("/dashboard/analytics/generate"),
  stream: () => client.get("/dashboard/stream"),
};
