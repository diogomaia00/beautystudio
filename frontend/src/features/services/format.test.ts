import { formatDuration, formatPrice } from "./format";

describe("formatPrice", () => {
  it("formats a decimal string as pt-PT euros", () => {
    // Non-breaking space + comma decimal in pt-PT locale.
    expect(formatPrice("17.50")).toMatch(/17,50\s?€/);
  });

  it("renders quote-only / null as 'Sob consulta'", () => {
    expect(formatPrice(null)).toBe("Sob consulta");
    expect(formatPrice("20.00", true)).toBe("Sob consulta");
  });

  it("falls back to 'Sob consulta' for an unparseable price", () => {
    expect(formatPrice("abc")).toBe("Sob consulta");
  });
});

describe("formatDuration", () => {
  it("formats sub-hour durations in minutes", () => {
    expect(formatDuration(15)).toBe("15 min");
    expect(formatDuration(45)).toBe("45 min");
  });

  it("formats whole hours", () => {
    expect(formatDuration(60)).toBe("1h");
    expect(formatDuration(120)).toBe("2h");
  });

  it("formats hours + minutes with zero-padding", () => {
    expect(formatDuration(75)).toBe("1h15");
    expect(formatDuration(150)).toBe("2h30");
    expect(formatDuration(65)).toBe("1h05");
  });
});
