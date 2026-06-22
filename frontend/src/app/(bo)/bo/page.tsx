"use client";

import Link from "next/link";

import PageHeader from "@/components/layouts/PageHeader";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";

import styles from "./dashboard.module.css";

interface QuickLink {
  href: string;
  label: string;
  description: string;
}

const QUICK_LINKS: QuickLink[] = [
  { href: "/bo/agenda", label: "Agenda", description: "Marcações por dia: marcar como feito, falta, cancelar ou remarcar." },
  { href: "/bo/clientes", label: "Clientes", description: "Pesquisar clientes, histórico, durações personalizadas e lista negra." },
  { href: "/bo/servicos", label: "Serviços", description: "Gerir serviços, preços, orçamento e descontos sazonais." },
  { href: "/bo/horarios", label: "Horários", description: "Horário semanal, pausas e ausências." },
  { href: "/bo/lista-espera", label: "Lista de espera", description: "Pedidos em lista de espera e pedidos personalizados." },
  { href: "/bo/formacoes", label: "Formações", description: "Formações da equipa apresentadas na página pública." },
  { href: "/bo/relatorios", label: "Relatórios", description: "Relatórios mensais: horas, marcações e receita." },
  { href: "/bo/alertas", label: "Alertas", description: "Avisos internos: lista de espera e pedidos personalizados." },
];

export default function BackOfficePage() {
  const { data: user } = useCurrentUser();

  return (
    <div className={styles.page}>
      <PageHeader
        title={user ? `Olá, ${user.first_name}` : "Back Office"}
        subtitle="Gere as marcações, os serviços, a equipa e os relatórios do Beauty Studio."
      />

      <ul className={styles.cards}>
        {QUICK_LINKS.map((link) => (
          <li key={link.href}>
            <Link href={link.href} className={styles.card}>
              <span className={styles.cardLabel}>{link.label}</span>
              <span className={styles.cardDesc}>{link.description}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
