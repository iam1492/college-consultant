import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/upload',
        destination: 'http://127.0.0.1:9000/upload',
      },
    ]
  },
};

export default nextConfig;
