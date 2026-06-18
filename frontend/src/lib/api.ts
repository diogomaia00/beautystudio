const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/v1";
const BO_API_BASE = process.env.NEXT_PUBLIC_BO_API_URL ?? "/bo/v1";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw Object.assign(new Error("API error"), { status: res.status, data: error });
  }

  return res.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(`${API_BASE}${path}`),
  post: <T>(path: string, body: unknown) =>
    request<T>(`${API_BASE}${path}`, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(`${API_BASE}${path}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(`${API_BASE}${path}`, { method: "DELETE" }),
};

export const boApiClient = {
  get: <T>(path: string) => request<T>(`${BO_API_BASE}${path}`),
  post: <T>(path: string, body: unknown) =>
    request<T>(`${BO_API_BASE}${path}`, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(`${BO_API_BASE}${path}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(`${BO_API_BASE}${path}`, { method: "DELETE" }),
};
