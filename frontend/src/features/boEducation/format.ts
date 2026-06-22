import type { EducationType } from "@/features/staff/types";

import { EDUCATION_TYPES } from "./types";

const dateFormatter = new Intl.DateTimeFormat("pt-PT", { dateStyle: "long" });

/** pt-PT label for an education type. */
export function educationTypeLabel(type: EducationType): string {
  return EDUCATION_TYPES.find((t) => t.value === type)?.label ?? type;
}

/** Format an ISO/YYYY-MM-DD date as a pt-PT long date. */
export function formatDate(iso: string): string {
  // Anchor date-only strings to midday UTC to avoid timezone day-shifts.
  const value = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? `${iso}T12:00:00` : iso;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return iso;
  return dateFormatter.format(date);
}
