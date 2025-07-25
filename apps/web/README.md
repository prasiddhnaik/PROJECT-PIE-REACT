This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Environment Setup

Before running the web application you need to configure the backend service URL.

1. Copy the provided environment template:

```bash
cp env.example .env.local
```

2. Edit `.env.local` and adjust `NEXT_PUBLIC_BACKEND_URL` as required.

| Scenario | Suggested value |
|----------|-----------------|
| Local monolithic backend started via `start.sh` | `http://localhost:8001` |
| Docker Compose stack (API-Gateway exposed on host) | `http://localhost:8001` |
| Custom port / remote environment | `https://api.my-domain.com` |

The frontend reads this variable at build/runtime to construct all API requests. A mis-configured value is the most common cause of "TypeError: Failed to fetch" errors.

> ℹ️  After editing the env file you **must restart** the dev server for changes to take effect.

---
