import type { Metadata } from "next";
import Link from "next/link";

import LoginForm from "@/features/auth/components/LoginForm";

import styles from "../auth.module.css";

export const metadata: Metadata = {
  title: "Entrar — Beauty Studio",
};

export default function LoginPage() {
  return (
    <main className={styles.page}>
      <Link href="/" className={styles.brand}>
        Beauty Studio
      </Link>
      <LoginForm />
    </main>
  );
}
