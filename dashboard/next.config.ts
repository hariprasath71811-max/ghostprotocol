import type { NextConfig } from "next";
import path from "node:path";

// Static export so the same build can be hosted on GitHub Pages.
// Set NEXT_PUBLIC_BASE_PATH=/repo-name only for project pages.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  basePath,
  assetPrefix: basePath || undefined,
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
