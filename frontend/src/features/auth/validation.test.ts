import {
  MIN_SIGNUP_AGE_YEARS,
  MSISDN_PATTERN,
  OTP_PATTERN,
  todayISO,
  validateBirthday,
} from "./validation";

/** YYYY-MM-DD for a date `years`/`days` offset from today. */
function isoFromToday({ years = 0, days = 0 }: { years?: number; days?: number }): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - years);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

describe("MSISDN_PATTERN", () => {
  it("accepts E.164-ish numbers", () => {
    expect(MSISDN_PATTERN.test("+351912345678")).toBe(true);
    expect(MSISDN_PATTERN.test("351912345678")).toBe(true);
  });
  it("rejects malformed numbers", () => {
    expect(MSISDN_PATTERN.test("0912")).toBe(false); // leading zero
    expect(MSISDN_PATTERN.test("abc")).toBe(false);
    expect(MSISDN_PATTERN.test("+1")).toBe(false); // too short
  });
});

describe("OTP_PATTERN", () => {
  it("matches exactly six digits", () => {
    expect(OTP_PATTERN.test("123456")).toBe(true);
    expect(OTP_PATTERN.test("12345")).toBe(false);
    expect(OTP_PATTERN.test("1234567")).toBe(false);
    expect(OTP_PATTERN.test("12a456")).toBe(false);
  });
});

describe("todayISO", () => {
  it("returns today's local date as YYYY-MM-DD", () => {
    expect(todayISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

describe("validateBirthday", () => {
  it("accepts an adult birthday", () => {
    expect(validateBirthday(isoFromToday({ years: 30 }))).toBe(true);
  });

  it("rejects an empty value", () => {
    expect(validateBirthday("")).toMatch(/data de nascimento/i);
  });

  it("rejects a future date", () => {
    expect(validateBirthday(isoFromToday({ days: 5 }))).toMatch(/futuro/i);
  });

  it(`rejects someone younger than ${MIN_SIGNUP_AGE_YEARS}`, () => {
    expect(validateBirthday(isoFromToday({ years: 8 }))).toMatch(/pelo menos/i);
  });

  it("accepts exactly the minimum age", () => {
    // One day past the Nth birthday is unambiguously old enough.
    expect(validateBirthday(isoFromToday({ years: MIN_SIGNUP_AGE_YEARS, days: -1 }))).toBe(true);
  });

  it("rejects an unparseable date", () => {
    expect(validateBirthday("not-a-date")).toMatch(/inválida/i);
  });
});
