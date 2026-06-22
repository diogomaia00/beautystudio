"use client";

import Button from "@/components/ui/Button";
import Badge from "@/features/bo/shared/Badge";
import type { StaffEducation } from "@/features/staff/types";

import { educationTypeLabel, formatDate } from "../format";

import panel from "@/features/bo/shared/panel.module.css";

interface EducationsTableProps {
  educations: StaffEducation[];
  onEdit: (education: StaffEducation) => void;
  onDelete: (education: StaffEducation) => void;
  /** Id currently being deleted (disables its row actions). */
  deletingId?: string | null;
}

export default function EducationsTable({
  educations,
  onEdit,
  onDelete,
  deletingId,
}: EducationsTableProps) {
  return (
    <div className={panel.tableWrap}>
      <table className={panel.table}>
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Título</th>
            <th>Entidade</th>
            <th>Data</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {educations.map((education) => (
            <tr key={education.id}>
              <td>
                <Badge tone="info">
                  {educationTypeLabel(education.education_type)}
                </Badge>
              </td>
              <td>{education.title}</td>
              <td>{education.provider}</td>
              <td>{formatDate(education.completed_on)}</td>
              <td>
                <div className={panel.actions}>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onEdit(education)}
                  >
                    Editar
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onDelete(education)}
                    disabled={deletingId === education.id}
                  >
                    {deletingId === education.id ? "A eliminar…" : "Eliminar"}
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
