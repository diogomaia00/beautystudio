"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import { useLogout } from "@/features/auth/hooks/useAuthActions";
import { CLINIC, NAV_LINKS } from "@/shared/constants/site";

import styles from "./Navbar.module.css";

function AuthActions() {
  const router = useRouter();
  const { data: user, isLoading } = useCurrentUser();
  const logout = useLogout();

  if (isLoading) return <span className={styles.authPlaceholder} aria-hidden="true" />;

  if (user) {
    return (
      <div className={styles.auth}>
        <Link href="/perfil" className={styles.authName}>
          Olá, {user.first_name}
        </Link>
        <button
          type="button"
          className={styles.authButton}
          disabled={logout.isPending}
          onClick={() =>
            logout.mutate(undefined, { onSuccess: () => router.push("/") })
          }
        >
          Sair
        </button>
      </div>
    );
  }

  return (
    <Link href="/login" className={styles.authButton}>
      Entrar
    </Link>
  );
}

export default function Navbar() {
  const pathname = usePathname();
  const { data: user } = useCurrentUser();

  // Clients get a "Marcações" link to their own appointments.
  const links =
    user?.role === "client"
      ? [...NAV_LINKS, { href: "/marcacoes", label: "Marcações" }]
      : NAV_LINKS;

  return (
    <header className={styles.header}>
      <nav className={styles.nav} aria-label="Navegação principal">
        <Link href="/" className={styles.logo} aria-label={`${CLINIC.name} — início`}>
          {CLINIC.name}
        </Link>

        <ul className={styles.links}>
          {links.map((link) => {
            const isActive =
              link.href === "/"
                ? pathname === "/"
                : pathname.startsWith(link.href);
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={styles.link}
                  aria-current={isActive ? "page" : undefined}
                  data-active={isActive || undefined}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>

        <AuthActions />
      </nav>
    </header>
  );
}
