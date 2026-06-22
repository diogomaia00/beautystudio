import type { Ref, SelectHTMLAttributes } from "react";

import styles from "./Input.module.css";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean;
  ref?: Ref<HTMLSelectElement>;
}

/** Design-system select, sharing the Input styling. Works with react-hook-form register(). */
export default function Select({ invalid, className, children, ...rest }: SelectProps) {
  const cls = [styles.input, invalid ? styles.invalid : "", className]
    .filter(Boolean)
    .join(" ");
  return (
    <select className={cls} aria-invalid={invalid || undefined} {...rest}>
      {children}
    </select>
  );
}
