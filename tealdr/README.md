# TeaL;DR Website

Official website for TeaL;DR Discord AI Search Bot.

## Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
npm run build
npm start
```

## Deploy

This Next.js app can be deployed to:
- Vercel (recommended)
- Netlify
- Any Node.js hosting platform

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Custom fonts** - JetBrains Mono, Space Mono, Outfit

## Features

- ✅ Responsive design
- ✅ Dark theme with custom color palette
- ✅ Smooth animations and transitions
- ✅ Command reference with examples
- ✅ Terms of Service page
- ✅ Privacy Policy page
- ✅ SEO optimized

## Customization

Update the Discord OAuth2 link in:
- `src/components/Navigation.tsx`
- `src/app/page.tsx`

Replace `YOUR_CLIENT_ID` with your actual Discord bot client ID.

## License

MIT
