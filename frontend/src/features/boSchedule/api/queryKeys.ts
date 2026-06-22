/** Stable query keys for the BO schedule feature, all scoped by staff id. */
export const scheduleKeys = {
  all: ["bo-schedule"] as const,
  schedule: (staffId: string) => [...scheduleKeys.all, "schedule", staffId] as const,
  breaks: (staffId: string) => [...scheduleKeys.all, "breaks", staffId] as const,
  timeOff: (staffId: string) => [...scheduleKeys.all, "time-off", staffId] as const,
};
