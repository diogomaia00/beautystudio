"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Modal from "@/components/ui/Modal";
import Select from "@/components/ui/Select";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import type { AppointmentActions } from "../hooks/useAppointmentActions";
import type { BoAppointment, NailArtOption } from "../types";

const NONE_VALUE = "none";

/** Map the Select string value to the API's nullable nail-art option. */
function toOption(value: string): NailArtOption {
  if (value === "simple" || value === "complex") return value;
  return null;
}

interface NailArtModalProps {
  appointment: BoAppointment;
  actions: AppointmentActions;
  onClose: () => void;
}

/** Staff-only edit of the nail-art option (simple ↔ complex ↔ none). */
export default function NailArtModal({
  appointment,
  actions,
  onClose,
}: NailArtModalProps) {
  const { setNailArtMutation } = actions;
  const [value, setValue] = useState<string>(
    appointment.nail_art_option ?? NONE_VALUE,
  );
  const [error, setError] = useState<string | null>(null);

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setNailArtMutation.mutate(
      { id: appointment.id, nail_art_option: toOption(value) },
      {
        onSuccess: onClose,
        onError: (err) =>
          setError(apiErrorMessage(err, "Não foi possível atualizar a nail art.")),
      },
    );
  };

  return (
    <Modal title="Editar nail art" onClose={onClose}>
      <form onSubmit={onSubmit}>
        <Field
          label="Opção de nail art"
          htmlFor="nail-art-option"
          error={error ?? undefined}
        >
          <Select
            id="nail-art-option"
            value={value}
            invalid={!!error}
            onChange={(e) => setValue(e.target.value)}
          >
            <option value="simple">Simples (+15 min)</option>
            <option value="complex">Complexa (+30 min)</option>
            <option value={NONE_VALUE}>Sem nail art</option>
          </Select>
        </Field>
        <div className={panel.actions}>
          <Button type="submit" disabled={setNailArtMutation.isPending}>
            {setNailArtMutation.isPending ? "A guardar…" : "Guardar"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </Modal>
  );
}
