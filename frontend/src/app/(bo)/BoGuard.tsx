"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import type { ReactNode } from "react";

import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";

import styles from "./bo.module.css";

/**
 * Gates the back office to authenticated staff/admin. Clients and signed-out
 * visitors are bounced to the login page. Authorization is still enforced
 * server-side on every `/bo/v1/` endpoint (IsStaffMember); this is UX only.
 */
export default function BoGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { data: user, isLoading } = useCurrentUser();
  const allowed = user?.role === "staff" || user?.role === "admin";

  useEffect(() => {
    if (isLoading) return;
    if (!user) {
      router.replace("/login");
    } else if (!allowed) {
      // A signed-in client has no place in the BO.
      router.replace("/");
    }
  }, [isLoading, user, allowed, router]);

  if (isLoading) {
    return (
      <div className={styles.gate} role="status" aria-live="polite">
        A carregar…
      </div>
    );
  }

  if (!allowed) {
    return (
      <div className={styles.gate} role="status" aria-live="polite">
        A redirecionar…
      </div>
    );
  }

  return <>{children}</>;
}
