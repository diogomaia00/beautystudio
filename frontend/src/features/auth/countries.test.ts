import {
  DEFAULT_COUNTRY,
  COUNTRIES,
  composeE164,
  digitsOnly,
  parseE164,
} from "./countries";

describe("digitsOnly", () => {
  it("strips everything except digits", () => {
    expect(digitsOnly("+351 912 345 678")).toBe("351912345678");
    expect(digitsOnly("(91) 2-34")).toBe("91234");
    expect(digitsOnly("abc")).toBe("");
  });
});

describe("composeE164", () => {
  it("builds an E.164 number from country + national part", () => {
    const pt = COUNTRIES.find((c) => c.iso === "PT")!;
    expect(composeE164(pt, "912345678")).toBe("+351912345678");
  });

  it("ignores non-digit characters in the national part", () => {
    const pt = COUNTRIES.find((c) => c.iso === "PT")!;
    expect(composeE164(pt, "912 345 678")).toBe("+351912345678");
  });

  it("returns an empty string when the national part is blank", () => {
    expect(composeE164(DEFAULT_COUNTRY, "")).toBe("");
    expect(composeE164(DEFAULT_COUNTRY, "   ")).toBe("");
  });
});

describe("parseE164", () => {
  it("splits a full number into the longest-matching country + national part", () => {
    const { country, national } = parseE164("+351912345678");
    expect(country.iso).toBe("PT");
    expect(national).toBe("912345678");
  });

  it("prefers the longest dial-code prefix", () => {
    // 351 (PT) must win over 35 (no country) / 3 etc.
    expect(parseE164("351912345678").country.iso).toBe("PT");
    // 1 is shared by US/CA — the first match (US) is returned deterministically.
    expect(parseE164("+15551234567").country.dial).toBe("1");
  });

  it("falls back to the default country for an empty or unknown number", () => {
    expect(parseE164("").country).toBe(DEFAULT_COUNTRY);
    expect(parseE164(undefined).national).toBe("");
  });

  it("round-trips with composeE164", () => {
    const original = "+34666777888";
    const { country, national } = parseE164(original);
    expect(composeE164(country, national)).toBe(original);
  });
});
