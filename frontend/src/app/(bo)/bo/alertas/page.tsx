"use client";

import { useState } from "react";

import PageHeader from "@/components/layouts/PageHeader";
import panel from "@/features/bo/shared/panel.module.css";
import AlertsList from "@/features/boAlerts/components/AlertsList";

export default function AlertasPage() {
  const [unreadOnly, setUnreadOnly] = useState(false);

  return (
    <div className={panel.page}>
      <PageHeader
        title="Alertas"
        subtitle="Notificações do back office: entradas na lista de espera e pedidos personalizados."
      />

      <div className={panel.toolbar}>
        <label className={panel.toolbarPush}>
          <input
            type="checkbox"
            checked={unreadOnly}
            onChange={(e) => setUnreadOnly(e.target.checked)}
          />{" "}
          Apenas não lidos
        </label>
      </div>

      <AlertsList unreadOnly={unreadOnly} />
    </div>
  );
}
