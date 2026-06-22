import { fireEvent, render, screen } from "@testing-library/react";

import Button from "./Button";

describe("Button", () => {
  it("renders a native button and forwards onClick", () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Guardar</Button>);
    const button = screen.getByRole("button", { name: "Guardar" });
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("respects the disabled attribute", () => {
    const onClick = jest.fn();
    render(
      <Button onClick={onClick} disabled>
        Guardar
      </Button>,
    );
    const button = screen.getByRole("button", { name: "Guardar" });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("renders a link when href is provided", () => {
    render(<Button href="/agendar">Agendar</Button>);
    const link = screen.getByRole("link", { name: "Agendar" });
    expect(link).toHaveAttribute("href", "/agendar");
  });

  it("forwards the type attribute", () => {
    render(<Button type="submit">Enviar</Button>);
    expect(screen.getByRole("button", { name: "Enviar" })).toHaveAttribute(
      "type",
      "submit",
    );
  });
});

