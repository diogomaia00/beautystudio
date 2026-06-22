// Next.js 16 ships native ESLint flat configs from `eslint-config-next`.
// Import them directly — the old `@eslint/eslintrc` FlatCompat shim is no longer
// needed and crashes under ESLint 9 ("Converting circular structure to JSON").
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypeScript from "eslint-config-next/typescript";

const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypeScript,

  // CommonJS config files (jest.config.js, etc.) legitimately use `require()`.
  // Scope off the TS no-require rule there instead of rewriting them to ESM.
  {
    files: ["**/*.config.js", "**/*.cjs"],
    rules: {
      "@typescript-eslint/no-require-imports": "off",
    },
  },

  // `react-hooks/incompatible-library` is a React Compiler readiness rule
  // (bundled in eslint-plugin-react-hooks@7). It fires on react-hook-form's
  // documented `watch()` API — a false positive with no legitimate per-site
  // signal — so it is turned off globally. The related `set-state-in-effect`
  // rule is intentionally LEFT ON so it keeps guarding new code; the single
  // legitimate exception is annotated inline in ScheduleEditor.tsx. Revisit
  // both if/when the React Compiler is adopted (no `experimental.reactCompiler`
  // in next.config.ts today).
  {
    rules: {
      "react-hooks/incompatible-library": "off",
    },
  },
];

export default eslintConfig;
