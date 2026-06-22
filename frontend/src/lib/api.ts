const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/v1";
const BO_API_BASE = process.env.NEXT_PUBLIC_BO_API_URL ?? "/bo/v1";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

/** DRF error envelope: { errors, status_code } (see backend/common/utils.py). */
export interface ApiError extends Error {
  status: number;
  data: unknown;
}

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

let csrfPrimed = false;

/** Ensure the `csrftoken` cookie exists before an unsafe request (SessionAuth + CSRF). */
async function ensureCsrfCookie(): Promise<void> {
  if (getCookie("csrftoken") || csrfPrimed) return;
  csrfPrimed = true;
  await fetch(`${API_BASE}/auth/csrf/`, { credentials: "include" });
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };

  if (!SAFE_METHODS.has(method)) {
    await ensureCsrfCookie();
    const token = getCookie("csrftoken");
    if (token) headers["X-CSRFToken"] = token;
  }

  const res = await fetch(url, { credentials: "include", headers, ...init });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw Object.assign(new Error("API error"), { status: res.status, data });
  }

  // 204 No Content (e.g. logout) has no body to parse.
  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

function makeClient(base: string) {
  return {
    get: <T>(path: string) => request<T>(`${base}${path}`),
    post: <T>(path: string, body?: unknown) =>
      request<T>(`${base}${path}`, {
        method: "POST",
        body: body === undefined ? undefined : JSON.stringify(body),
      }),
    patch: <T>(path: string, body: unknown) =>
      request<T>(`${base}${path}`, { method: "PATCH", body: JSON.stringify(body) }),
    delete: <T>(path: string) => request<T>(`${base}${path}`, { method: "DELETE" }),
  };
}

export const apiClient = makeClient(API_BASE);
export const boApiClient = makeClient(BO_API_BASE);

/** Best-effort human message from an API error (or generic fallback). */
export function apiErrorMessage(error: unknown, fallback = "Algo correu mal. Tenta novamente."): string {
  const data = (error as ApiError | undefined)?.data as
    | { errors?: unknown }
    | undefined;
  const errors = data?.errors;
  if (typeof errors === "string") return errors;
  if (errors && typeof errors === "object") {
    const record = errors as Record<string, unknown>;
    const detail = record.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && typeof detail[0] === "string") return detail[0];
    // First field error.
    for (const value of Object.values(record)) {
      if (typeof value === "string") return value;
      if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    }
  }
  return fallback;
}
