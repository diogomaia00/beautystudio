import type { NotificationChannel } from "@/features/auth/types";

import type { Client } from "./types";

const dateFormatter = new Intl.DateTimeFormat("pt-PT", {
  timeZone: "Europe/Lisbon",
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const CHANNEL_LABELS: Record<NotificationChannel, string> = {
  whatsapp: "WhatsApp",
  sms: "SMS",
  email: "Email",
};

/** Human label for a preferred notification channel. */
export function formatChannel(channel: NotificationChannel): string {
  return CHANNEL_LABELS[channel];
}

/** Localized pt-PT date from an ISO date string (YYYY-MM-DD). */
export function formatDate(iso: string): string {
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return iso;
  return dateFormatter.format(date);
}

/** "First Last" for a client. */
export function fullName(client: Pick<Client, "first_name" | "last_name">): string {
  return `${client.first_name} ${client.last_name}`.trim();
}
