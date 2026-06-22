/**
 * Static site-wide constants for the client app.
 *
 * The clinic `location` mirrors `system_settings.location` in the backend
 * (single source of truth there); it is duplicated here so the public pages
 * render without a backend round-trip. Keep both in sync if the address changes.
 */

export interface NavLink {
  href: string;
  label: string;
}

/** Primary navigation, rendered as text links in the navbar. */
export const NAV_LINKS: NavLink[] = [
  { href: "/", label: "Início" },
  { href: "/agendar", label: "Agendar" },
  { href: "/servicos", label: "Serviços" },
  { href: "/equipa", label: "Equipa" },
];

export const CLINIC = {
  name: "Beauty Studio",
  /** Mirrors DB system_settings.location. */
  location: "Rua Vila Vieira 17, Ançã",
} as const;
