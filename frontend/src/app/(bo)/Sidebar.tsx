"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useLogout } from "@/features/auth/hooks/useAuthActions";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import { BO_NAV_LINKS } from "@/shared/constants/bo";
import { CLINIC } from "@/shared/constants/site";

import styles from "./Sidebar.module.css";

function isActiveLink(pathname: string, href: string): boolean {
  if (href === "/bo") return pathname === "/bo";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** BO navigation rail: logo, page links (text only), staff picker, logout. */
export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: user } = useCurrentUser();
  const logout = useLogout();
  const { staffId, staffList, setStaffId, isAdmin } = useActiveStaff();

  return (
    <aside className={styles.sidebar} aria-label="Navegação do back office">
      <div className={styles.brand}>
        <Link href="/bo" className={styles.logo}>
          {CLINIC.name}
        </Link>
        <span className={styles.tag}>Back Office</span>
      </div>

      <nav className={styles.nav} aria-label="Páginas do back office">
        <ul className={styles.links}>
          {BO_NAV_LINKS.map((link) => {
            const active = isActiveLink(pathname, link.href);
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={styles.link}
                  aria-current={active ? "page" : undefined}
                  data-active={active || undefined}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className={styles.footer}>
        {isAdmin && staffList.length > 0 ? (
          <label className={styles.staffPicker}>
            <span className={styles.staffLabel}>Equipa</span>
            <select
              className={styles.staffSelect}
              value={staffId ?? ""}
              onChange={(e) => setStaffId(e.target.value)}
            >
              {staffList.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.first_name} {s.last_name}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        {user ? <p className={styles.who}>{user.first_name} {user.last_name}</p> : null}

        <button
          type="button"
          className={styles.logout}
          disabled={logout.isPending}
          onClick={() => logout.mutate(undefined, { onSuccess: () => router.push("/login") })}
        >
          Sair
        </button>
      </div>
    </aside>
  );
}
