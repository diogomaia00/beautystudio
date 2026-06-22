// Jest config via next/jest — uses Next's built-in SWC transform (no ts-node /
// @swc/core needed) and auto-mocks CSS modules + static assets. See frontend.md
// (TESTING) and Phase 6.1.
const nextJest = require("next/jest");

const createJestConfig = nextJest({ dir: "./" });

/** @type {import('jest').Config} */
const config = {
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  // Mirror the tsconfig "@/*" path alias.
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  // Only our own source — never node_modules.
  testPathIgnorePatterns: ["/node_modules/", "/.next/"],
};

module.exports = createJestConfig(config);
