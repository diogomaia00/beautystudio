import { fireEvent, render, screen } from "@testing-library/react";

import type { AppointmentActions } from "../hooks/useAppointmentActions";
import type { BoAppointment } from "../types";
import NailArtModal from "./NailArtModal";

function makeAppointment(overrides: Partial<BoAppointment> = {}): BoAppointment {
  return {
    id: "appt-1",
    batch: null,
    client: "c-1",
    client_name: "Ana Costa",
    client_msisdn: "+351912345678",
    staff: "s-1",
    service: { id: "svc-1", name: "Manicure", is_nail_service: true },
    status: "booked",
    start_at: "2026-07-01T09:00:00Z",
    end_at: "2026-07-01T10:00:00Z",
    notes: "",
    nail_art_option: "simple",
    has_nail_art: true,
    price_snapshot: "20.00",
    is_quote_only_snapshot: false,
    duration_minutes_snapshot: 75,
    cancel_reason: null,
    created_at: "2026-06-01T09:00:00Z",
    ...overrides,
  };
}

function makeActions(isPending = false): AppointmentActions {
  return {
    setNailArtMutation: { mutate: jest.fn(), isPending },
  } as unknown as AppointmentActions;
}

describe("NailArtModal (staff-only nail-art edit)", () => {
  it("pre-selects the appointment's current nail-art option", () => {
    render(
      <NailArtModal
        appointment={makeAppointment({ nail_art_option: "complex" })}
        actions={makeActions()}
        onClose={jest.fn()}
      />,
    );
    expect(screen.getByLabelText("Opção de nail art")).toHaveValue("complex");
  });

  it("submits the chosen option through the mutation", () => {
    const actions = makeActions();
    render(
      <NailArtModal
        appointment={makeAppointment({ nail_art_option: "simple" })}
        actions={actions}
        onClose={jest.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Opção de nail art"), {
      target: { value: "complex" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    expect(actions.setNailArtMutation.mutate).toHaveBeenCalledWith(
      { id: "appt-1", nail_art_option: "complex" },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it("maps the 'Sem nail art' option to null", () => {
    const actions = makeActions();
    render(
      <NailArtModal
        appointment={makeAppointment()}
        actions={actions}
        onClose={jest.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Opção de nail art"), {
      target: { value: "none" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

    expect(actions.setNailArtMutation.mutate).toHaveBeenCalledWith(
      { id: "appt-1", nail_art_option: null },
      expect.anything(),
    );
  });

  it("disables the submit button while the mutation is pending", () => {
    render(
      <NailArtModal
        appointment={makeAppointment()}
        actions={makeActions(true)}
        onClose={jest.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "A guardar…" })).toBeDisabled();
  });
});
