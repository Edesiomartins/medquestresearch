import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Especifica o diretório raiz do projeto para evitar aviso de múltiplos lockfiles
  turbopack: {
    root: process.cwd(),
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
  // Headers para segurança (dados médicos)
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
        ],
      },
    ];
  },
  async rewrites() {
    // Não usa mais proxy - todas as chamadas vão direto para o Railway
    // NEXT_PUBLIC_API_BASE_URL = https://medquestresearch-api.up.railway.app
    return [];
  },
};

export default nextConfig;