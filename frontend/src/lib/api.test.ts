import { apiErrorMessage, type ApiError } from "./api";

function makeError(data: unknown): ApiError {
  return Object.assign(new Error("API error"), { status: 400, data }) as ApiError;
}

describe("apiErrorMessage", () => {
  it("returns a top-level string error", () => {
    expect(apiErrorMessage(makeError({ errors: "Conta bloqueada." }))).toBe(
      "Conta bloqueada.",
    );
  });

  it("returns the DRF `detail` message", () => {
    expect(apiErrorMessage(makeError({ errors: { detail: "Não encontrado." } }))).toBe(
      "Não encontrado.",
    );
  });

  it("returns the first item of a `detail` array", () => {
    expect(
      apiErrorMessage(makeError({ errors: { detail: ["Esse horário já foi ocupado."] } })),
    ).toBe("Esse horário já foi ocupado.");
  });

  it("returns the first field-level error", () => {
    expect(
      apiErrorMessage(makeError({ errors: { msisdn: ["Número inválido."] } })),
    ).toBe("Número inválido.");
  });

  it("falls back when there is no usable message", () => {
    expect(apiErrorMessage(makeError({}), "fallback")).toBe("fallback");
    expect(apiErrorMessage(undefined)).toMatch(/correu mal/i);
  });
});
