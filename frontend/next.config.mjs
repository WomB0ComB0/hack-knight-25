/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  poweredByHeader: false,
  swcMinify: true,
};

export default nextConfig;
