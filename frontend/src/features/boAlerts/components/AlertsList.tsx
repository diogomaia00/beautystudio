"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Badge from "@/features/bo/shared/Badge";
import type { BadgeTone } from "@/features/bo/shared/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import { useAlerts, useMarkAlertRead } from "../hooks/useAlerts";
import type { BoAlert, BoAlertType } from "../types";
import styles from "./alerts.module.css";

const TYPE_META: Record<BoAlertType, { label: string; tone: BadgeTone }> = {
  waitlist_join: { label: "Lista de espera", tone: "info" },
  custom_request: { label: "Pedido personalizado", tone: "accent" },
};

function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("pt-PT", {
    timeZone: "Europe/Lisbon",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

/** Single alert card. */
function AlertCard({
  alert,
  onRead,
  isPending,
}: {
  alert: BoAlert;
  onRead: (id: string) => void;
  isPending: boolean;
}) {
  const meta = TYPE_META[alert.alert_type];
  const unread = !alert.is_read;
  return (
    <article className={`${styles.item} ${unread ? styles.unread : ""}`}>
      <div className={styles.head}>
        <h3 className={`${styles.title} ${unread ? styles.titleUnread : ""}`}>
          {alert.title}
        </h3>
        <Badge tone={meta.tone}>{meta.label}</Badge>
        {unread ? <Badge tone="info">Por ler</Badge> : null}
      </div>
      <p className={styles.body}>{alert.body}</p>
      <div className={styles.meta}>
        <span className={styles.time}>{formatDateTime(alert.created_at)}</span>
        {unread ? (
          <Button
            variant="secondary"
            size="sm"
            disabled={isPending}
            onClick={() => onRead(alert.id)}
          >
            Marcar como lido
          </Button>
        ) : null}
      </div>
    </article>
  );
}

/** List of in-app BO alerts. Unread-filter toggle is owned by the page. */
export default function AlertsList({ unreadOnly }: { unreadOnly: boolean }) {
  const { data, isLoading, isError, error, refetch } = useAlerts(unreadOnly);
  const markRead = useMarkAlertRead();
  const [actionError, setActionError] = useState<string | null>(null);

  async function onRead(id: string) {
    setActionError(null);
    try {
      await markRead.mutateAsync(id);
    } catch (err) {
      setActionError(apiErrorMessage(err, "Não foi possível marcar como lido."));
    }
  }

  if (isLoading) return <LoadingState />;
  if (isError) {
    return (
      <ErrorState
        action={<Button onClick={() => void refetch()}>Tentar novamente</Button>}
      >
        {apiErrorMessage(error, "Não foi possível carregar os alertas.")}
      </ErrorState>
    );
  }
  if (!data || data.length === 0) {
    return (
      <EmptyState title="Sem alertas">
        {unreadOnly
          ? "Não há alertas por ler."
          : "Ainda não existem alertas."}
      </EmptyState>
    );
  }

  return (
    <>
      <div className={styles.list}>
        {data.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onRead={(id) => void onRead(id)}
            isPending={markRead.isPending}
          />
        ))}
      </div>
      {actionError ? (
        <p className={panel.feedbackError} role="alert">
          {actionError}
        </p>
      ) : null}
    </>
  );
}
