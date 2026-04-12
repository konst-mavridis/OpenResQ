import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn-icons-png.flaticon.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  redirects: async () => [
    {
      source: '/admin',
      destination: 'https://dashboard.openresq.org',
      permanent: false,
    },
    {
      source: '/admin/:path*',
      destination: 'https://dashboard.openresq.org/:path*',
      permanent: false,
    },
    {
      source: '/dashboard',
      destination: 'https://dashboard.openresq.org',
      permanent: false,
    },
    {
      source: '/dashboard/:path*',
      destination: 'https://dashboard.openresq.org/:path*',
      permanent: false,
    },
  ],
};

export default nextConfig;
