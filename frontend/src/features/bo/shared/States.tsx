import type { ReactNode } from "react";

import styles from "./states.module.css";

/** Centered "loading" placeholder for a data view. */
export function LoadingState({ label = "A carregar…" }: { label?: string }) {
  return (
    <div className={styles.state} role="status" aria-live="polite">
      {label}
    </div>
  );
}

/** Centered empty placeholder with an optional title + action. */
export function EmptyState({
  title,
  children,
  action,
}: {
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className={styles.state}>
      <p className={styles.title}>{title}</p>
      {children ? <p>{children}</p> : null}
      {action}
    </div>
  );
}

/** Centered error placeholder. */
export function ErrorState({
  title = "Não foi possível carregar",
  children,
  action,
}: {
  title?: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className={`${styles.state} ${styles.error}`} role="alert">
      <p className={`${styles.title} ${styles.errorTitle}`}>{title}</p>
      {children ? <p>{children}</p> : null}
      {action}
    </div>
  );
}
