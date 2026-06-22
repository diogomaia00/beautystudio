import { boApiClient } from "@/lib/api";

import type {
  Break,
  BreakInput,
  ScheduleEntry,
  ScheduleEntryInput,
  TimeOff,
  TimeOffInput,
} from "../types";

// ------------------------------------------------------------
// Weekly schedule (PUT — full replace)
// ------------------------------------------------------------
// The backend `BoStaffScheduleView` replaces the whole weekly schedule with a
// single `PUT` (verified in backend/apps/availability/views.py). The shared
// `boApiClient` only exposes get/post/patch/delete, so we issue the PUT here
// with a minimal helper that mirrors lib/api.ts's CSRF + credentials logic
// (SessionAuthentication + CSRF). We intentionally do NOT edit the shared
// client just to add a one-off verb.

const BO_API_BASE = process.env.NEXT_PUBLIC_BO_API_URL ?? "/bo/v1";

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** Ensure the `csrftoken` cookie exists before an unsafe request. */
async function ensureCsrfCookie(): Promise<void> {
  if (getCookie("csrftoken")) return;
  // Prime via the client API's CSRF endpoint (same as lib/api.ts).
  await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "/v1"}/auth/csrf/`, {
    credentials: "include",
  });
}

/** Replace the whole weekly schedule for a staff member (PUT). */
export async function replaceSchedule(
  staffId: string,
  entries: ScheduleEntryInput[],
): Promise<ScheduleEntry[]> {
  await ensureCsrfCookie();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getCookie("csrftoken");
  if (token) headers["X-CSRFToken"] = token;

  const res = await fetch(
    `${BO_API_BASE}/availability/staff/${encodeURIComponent(staffId)}/schedule/`,
    {
      method: "PUT",
      credentials: "include",
      headers,
      body: JSON.stringify({ entries }),
    },
  );

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    // Match the shape thrown by lib/api.ts so apiErrorMessage() can read it.
    throw Object.assign(new Error("API error"), { status: res.status, data });
  }
  return res.json() as Promise<ScheduleEntry[]>;
}

// ------------------------------------------------------------
// Breaks
// ------------------------------------------------------------

export function createBreak(staffId: string, input: BreakInput): Promise<Break> {
  return boApiClient.post<Break>(
    `/availability/staff/${encodeURIComponent(staffId)}/breaks/`,
    input,
  );
}

export function deleteBreak(staffId: string, breakId: string): Promise<void> {
  return boApiClient.delete<void>(
    `/availability/staff/${encodeURIComponent(staffId)}/breaks/${encodeURIComponent(breakId)}/`,
  );
}

// ------------------------------------------------------------
// Time-off
// ------------------------------------------------------------

export function createTimeOff(staffId: string, input: TimeOffInput): Promise<TimeOff> {
  return boApiClient.post<TimeOff>(
    `/availability/staff/${encodeURIComponent(staffId)}/time-off/`,
    input,
  );
}

export function deleteTimeOff(staffId: string, timeOffId: string): Promise<void> {
  return boApiClient.delete<void>(
    `/availability/staff/${encodeURIComponent(staffId)}/time-off/${encodeURIComponent(timeOffId)}/`,
  );
}
