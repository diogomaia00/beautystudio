import { fireEvent, render, screen } from "@testing-library/react";

import Modal from "./Modal";

describe("Modal", () => {
  it("renders an accessible dialog with the title and a close button", () => {
    render(
      <Modal title="Editar nail art" onClose={jest.fn()}>
        <p>conteúdo</p>
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(dialog).toHaveAttribute("aria-label", "Editar nail art");
    expect(screen.getByRole("button", { name: "Fechar" })).toBeInTheDocument();
    expect(screen.getByText("conteúdo")).toBeInTheDocument();
  });

  it("calls onClose when the close button is clicked", () => {
    const onClose = jest.fn();
    render(
      <Modal title="T" onClose={onClose}>
        x
      </Modal>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Fechar" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape is pressed", () => {
    const onClose = jest.fn();
    render(
      <Modal title="T" onClose={onClose}>
        x
      </Modal>,
    );
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("does not close when the dialog body is clicked", () => {
    const onClose = jest.fn();
    render(
      <Modal title="T" onClose={onClose}>
        <span>dentro</span>
      </Modal>,
    );
    fireEvent.click(screen.getByText("dentro"));
    expect(onClose).not.toHaveBeenCalled();
  });
});
