import type { InputHTMLAttributes, Ref } from "react";

import styles from "./Input.module.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
  ref?: Ref<HTMLInputElement>;
}

/** Design-system text input (contour, focus ring). Works with react-hook-form's register(). */
export default function Input({ invalid, className, ...rest }: InputProps) {
  const cls = [styles.input, invalid ? styles.invalid : "", className]
    .filter(Boolean)
    .join(" ");
  return <input className={cls} aria-invalid={invalid || undefined} {...rest} />;
}
