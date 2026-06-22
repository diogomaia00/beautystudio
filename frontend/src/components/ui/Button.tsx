import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./Button.module.css";

type Variant = "primary" | "secondary";
type Size = "sm" | "md" | "lg";

interface BaseProps {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: ReactNode;
}

type LinkProps = BaseProps & { href: string };

type NativeButtonProps = BaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & { href?: never };

function classes(variant: Variant, size: Size, className?: string): string {
  return [styles.button, styles[variant], styles[size], className]
    .filter(Boolean)
    .join(" ");
}

/**
 * Design-system button. Renders a Next `Link` when `href` is set, otherwise a
 * native `<button>` (forwards onClick, type, aria-*, disabled, …).
 */
export default function Button(props: LinkProps | NativeButtonProps) {
  if ("href" in props && typeof props.href === "string") {
    const { href, variant = "primary", size = "md", className, children } = props;
    return (
      <Link href={href} className={classes(variant, size, className)}>
        {children}
      </Link>
    );
  }

  const {
    variant = "primary",
    size = "md",
    className,
    children,
    ...rest
  } = props as NativeButtonProps;
  return (
    <button className={classes(variant, size, className)} {...rest}>
      {children}
    </button>
  );
}
