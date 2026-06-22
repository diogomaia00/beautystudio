import { formatDateTime, formatEur, monthLabel } from "./format";

describe("monthLabel", () => {
  it("maps 1-12 to pt-PT month names", () => {
    expect(monthLabel(1)).toBe("Janeiro");
    expect(monthLabel(3)).toBe("Março");
    expect(monthLabel(12)).toBe("Dezembro");
  });

  it("falls back to the number for out-of-range input", () => {
    expect(monthLabel(13)).toBe("13");
  });
});

describe("formatEur", () => {
  it("formats both numeric and decimal-string revenue (the report sends strings)", () => {
    expect(formatEur("55.00")).toMatch(/55,00\s?€/);
    expect(formatEur(22)).toMatch(/22,00\s?€/);
  });

  it("renders a dash for non-numeric values", () => {
    expect(formatEur("not-a-number")).toBe("—");
  });
});

describe("formatDateTime", () => {
  it("returns the raw input for an invalid ISO string", () => {
    expect(formatDateTime("nope")).toBe("nope");
  });

  it("formats a valid ISO datetime", () => {
    // Locale-specific, but must contain the year.
    expect(formatDateTime("2026-05-15T10:00:00Z")).toContain("2026");
  });
});
