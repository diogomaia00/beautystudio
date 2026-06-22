"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import PageHeader from "@/components/layouts/PageHeader";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import EducationFormModal from "@/features/boEducation/components/EducationFormModal";
import EducationsTable from "@/features/boEducation/components/EducationsTable";
import {
  useDeleteEducation,
  useEducations,
} from "@/features/boEducation/hooks/useEducations";
import type { StaffEducation } from "@/features/staff/types";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

type ModalState =
  | { kind: "none" }
  | { kind: "create" }
  | { kind: "edit"; education: StaffEducation };

export default function FormacoesPage() {
  const { staffId, isAdmin, isLoading } = useActiveStaff();
  const [modal, setModal] = useState<ModalState>({ kind: "none" });

  const educations = useEducations(staffId);
  const deleteEducation = useDeleteEducation(staffId ?? "");

  const closeModal = () => setModal({ kind: "none" });

  const handleDelete = (education: StaffEducation) => {
    if (!window.confirm(`Eliminar "${education.title}"?`)) return;
    deleteEducation.mutate(education.id);
  };

  return (
    <div className={panel.page}>
      <PageHeader
        title="Formações"
        subtitle="Formações, webinars e cursos da equipa — aparecem na página pública da equipa."
      />

      {isLoading ? (
        <LoadingState />
      ) : isAdmin && !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Seleciona um membro da equipa para gerir as formações.
        </EmptyState>
      ) : !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Não foi possível identificar o membro da equipa.
        </EmptyState>
      ) : (
        <>
          <div className={panel.toolbar}>
            <div className={panel.toolbarPush}>
              <Button type="button" onClick={() => setModal({ kind: "create" })}>
                Nova formação
              </Button>
            </div>
          </div>

          {deleteEducation.isError ? (
            <p className={panel.feedbackError} role="alert">
              {apiErrorMessage(
                deleteEducation.error,
                "Não foi possível eliminar a formação.",
              )}
            </p>
          ) : null}

          {educations.isLoading ? (
            <LoadingState label="A carregar formações…" />
          ) : educations.isError ? (
            <ErrorState
              action={
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => educations.refetch()}
                >
                  Tentar novamente
                </Button>
              }
            >
              {apiErrorMessage(
                educations.error,
                "Não foi possível carregar as formações.",
              )}
            </ErrorState>
          ) : (educations.data ?? []).length === 0 ? (
            <EmptyState
              title="Sem formações"
              action={
                <Button type="button" onClick={() => setModal({ kind: "create" })}>
                  Nova formação
                </Button>
              }
            >
              Ainda não há formações registadas para este membro da equipa.
            </EmptyState>
          ) : (
            <EducationsTable
              educations={educations.data ?? []}
              onEdit={(education) => setModal({ kind: "edit", education })}
              onDelete={handleDelete}
              deletingId={
                deleteEducation.isPending ? deleteEducation.variables : null
              }
            />
          )}
        </>
      )}

      {staffId && modal.kind === "create" ? (
        <EducationFormModal staffId={staffId} onClose={closeModal} />
      ) : null}

      {staffId && modal.kind === "edit" ? (
        <EducationFormModal
          staffId={staffId}
          education={modal.education}
          onClose={closeModal}
        />
      ) : null}
    </div>
  );
}
