/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for better deployment
  output: 'standalone',
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Optimize images
  images: {
    domains: ['localhost'],
    unoptimized: true, // For better compatibility with Render
  },
  
  // Disable x-powered-by header
  poweredByHeader: false,
  
  // Compress responses
  compress: true,
  
  // Enable experimental features
  experimental: {
    // Optimize for serverless deployment
    serverComponentsExternalPackages: [],
  },
  
  // Webpack configuration
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

export default nextConfig;