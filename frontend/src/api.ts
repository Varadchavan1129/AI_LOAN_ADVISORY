// Centralised API base. All backend routes are served under `/api`
// and routed to the FastAPI backend by the Kubernetes ingress.
const BASE = (import.meta.env.REACT_APP_BACKEND_URL ?? '').replace(/\/$/, '');

export const API = `${BASE}/api`;
