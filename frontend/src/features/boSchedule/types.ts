/** Back-office "Horários" domain types (staff weekly schedule, breaks, time-off). */

/** A recurring weekly schedule entry. Times are clock times ("HH:MM:SS"). */
export interface ScheduleEntry {
  id: string;
  weekday: number; // clinic encoding 1..7 (1=Sun … 7=Sat)
  start_time: string; // "HH:MM:SS"
  end_time: string;
}

/** Write payload for a single schedule entry (times as "HH:MM"). */
export interface ScheduleEntryInput {
  weekday: number;
  start_time: string; // "HH:MM"
  end_time: string;
}

/** A recurring daily break window (e.g. lunch). */
export interface Break {
  id: string;
  weekday: number;
  start_time: string; // "HH:MM:SS"
  end_time: string;
  reason: string;
}

/** Write payload for a break window. */
export interface BreakInput {
  weekday: number;
  start_time: string; // "HH:MM"
  end_time: string;
  reason: string;
}

/** A time-off period (vacation, sick leave, holiday). Timestamps are ISO UTC. */
export interface TimeOff {
  id: string;
  start_at: string; // ISO datetime
  end_at: string;
  reason: string;
}

/** Write payload for time-off (timestamps as ISO UTC). */
export interface TimeOffInput {
  start_at: string; // ISO datetime
  end_at: string;
  reason: string;
}

/**
 * Weekdays in display order (Mon → Sun) carrying the clinic storage codes
 * (1=Sun, 2=Mon … 7=Sat — NOT ISO). `value` is what the backend expects.
 */
export const WEEKDAYS: ReadonlyArray<{ value: number; label: string }> = [
  { value: 2, label: "Segunda" },
  { value: 3, label: "Terça" },
  { value: 4, label: "Quarta" },
  { value: 5, label: "Quinta" },
  { value: 6, label: "Sexta" },
  { value: 7, label: "Sábado" },
  { value: 1, label: "Domingo" },
];

/** Human label for a clinic weekday code. */
export function weekdayLabel(n: number): string {
  return WEEKDAYS.find((w) => w.value === n)?.label ?? String(n);
}
