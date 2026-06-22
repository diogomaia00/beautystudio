import type { ReactNode } from "react";

import styles from "./badge.module.css";

export type BadgeTone =
  | "neutral"
  | "success"
  | "warning"
  | "error"
  | "info"
  | "accent";

/** Small status pill used across BO tables and cards. */
export default function Badge({
  tone = "neutral",
  children,
}: {
  tone?: BadgeTone;
  children: ReactNode;
}) {
  return <span className={`${styles.badge} ${styles[tone]}`}>{children}</span>;
}
