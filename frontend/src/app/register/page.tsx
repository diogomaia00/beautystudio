import type { Metadata } from "next";
import Link from "next/link";

import RegisterForm from "@/features/auth/components/RegisterForm";

import styles from "../auth.module.css";

export const metadata: Metadata = {
  title: "Criar conta — Beauty Studio",
};

export default function RegisterPage() {
  return (
    <main className={styles.page}>
      <Link href="/" className={styles.brand}>
        Beauty Studio
      </Link>
      <RegisterForm />
    </main>
  );
}
