/**
 * Back-office navigation.
 *
 * Rendered as text links in the BO sidebar (logo on top, pages below). Staff
 * use the BO mostly on iPad, so the sidebar is a fixed left rail on tablet/
 * desktop and a scrollable top rail on mobile.
 */

export interface BoNavLink {
  href: string;
  label: string;
}

/** Ordered BO pages shown under the logo in the sidebar. */
export const BO_NAV_LINKS: BoNavLink[] = [
  { href: "/bo", label: "Início" },
  { href: "/bo/agenda", label: "Agenda" },
  { href: "/bo/clientes", label: "Clientes" },
  { href: "/bo/servicos", label: "Serviços" },
  { href: "/bo/horarios", label: "Horários" },
  { href: "/bo/lista-espera", label: "Lista de espera" },
  { href: "/bo/formacoes", label: "Formações" },
  { href: "/bo/relatorios", label: "Relatórios" },
  { href: "/bo/alertas", label: "Alertas" },
];
