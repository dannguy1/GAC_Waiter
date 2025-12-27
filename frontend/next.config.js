/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '8000',
                pathname: '/images/**',
            },
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '8000',
                pathname: '/downloaded_images/**',
            },
            {
                protocol: 'https',
                hostname: 'placehold.co',
            },
        ],
    },
    async rewrites() {
        return [
            {
                source: '/v1/:path*',
                destination: 'http://127.0.0.1:8000/v1/:path*',
            },
            {
                source: '/images/:path*',
                destination: 'http://127.0.0.1:8000/images/:path*',
            },
            {
                source: '/downloaded_images/:path*',
                destination: 'http://127.0.0.1:8000/downloaded_images/:path*',
            },
        ];
    },
}

module.exports = nextConfig
