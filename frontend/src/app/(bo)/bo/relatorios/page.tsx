"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Modal from "@/components/ui/Modal";
import PageHeader from "@/components/layouts/PageHeader";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import GenerateReportForm from "@/features/boReports/components/GenerateReportForm";
import ReportCard from "@/features/boReports/components/ReportCard";
import ReportsList from "@/features/boReports/components/ReportsList";
import { monthLabel } from "@/features/boReports/format";
import { useReports } from "@/features/boReports/hooks/useReports";
import type { MonthlyReport } from "@/features/boReports/types";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

export default function RelatoriosPage() {
  const { staffId, isAdmin, isLoading } = useActiveStaff();
  const [selected, setSelected] = useState<MonthlyReport | null>(null);

  // Admin must scope by staff; staff use their own id (param omitted).
  const staffParam = isAdmin ? (staffId ?? undefined) : undefined;
  const reportsEnabled = !isLoading && (!isAdmin || !!staffId);
  const reports = useReports(staffParam, reportsEnabled);

  return (
    <div className={panel.page}>
      <PageHeader
        title="Relatórios"
        subtitle={
          isAdmin
            ? "Relatórios mensais por membro da equipa (escolhe o membro na barra lateral)."
            : "Os teus relatórios mensais: horas, marcações, clientes e receita."
        }
      />

      {isLoading ? (
        <LoadingState />
      ) : isAdmin && !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Seleciona um membro da equipa para ver e gerar relatórios.
        </EmptyState>
      ) : (
        <>
          <GenerateReportForm
            staffId={staffParam}
            isAdmin={isAdmin}
            onGenerated={(report) => setSelected(report)}
          />

          <section className={panel.card}>
            <h2 className={panel.cardTitle}>Relatórios gerados</h2>

            {reports.isLoading ? (
              <LoadingState label="A carregar relatórios…" />
            ) : reports.isError ? (
              <ErrorState
                action={
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => reports.refetch()}
                  >
                    Tentar novamente
                  </Button>
                }
              >
                {apiErrorMessage(
                  reports.error,
                  "Não foi possível carregar os relatórios.",
                )}
              </ErrorState>
            ) : (reports.data ?? []).length === 0 ? (
              <EmptyState title="Sem relatórios">
                Ainda não foram gerados relatórios. Usa o formulário acima para
                gerar o primeiro.
              </EmptyState>
            ) : (
              <ReportsList
                reports={reports.data ?? []}
                onView={(report) => setSelected(report)}
              />
            )}
          </section>
        </>
      )}

      {selected ? (
        <Modal
          title={`Relatório de ${monthLabel(selected.month)} de ${selected.year}`}
          onClose={() => setSelected(null)}
        >
          <ReportCard report={selected} />
        </Modal>
      ) : null}
    </div>
  );
}
