import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Hide the Next.js dev-tools indicator/logo overlay.
  devIndicators: false,
  // Local dev only: proxy API calls to the backend so `npm run dev` works
  // without NGINX (which fronts /v1 + /bo/v1 in real deployments). Opt-in via
  // BACKEND_ORIGIN (e.g. http://localhost:8000). No-op when unset.
  async rewrites() {
    const backend = process.env.BACKEND_ORIGIN;
    if (!backend) return [];
    return [
      { source: "/v1/:path*", destination: `${backend}/v1/:path*` },
      { source: "/bo/v1/:path*", destination: `${backend}/bo/v1/:path*` },
    ];
  },
};

export default nextConfig;
