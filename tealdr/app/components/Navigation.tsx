'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-tea-darker/95 backdrop-blur-md border-b border-tea-light/50' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-tea-accent to-tea-green rounded-lg flex items-center justify-center font-mono font-bold text-tea-darker group-hover:scale-110 transition-transform">
              T
            </div>
            <span className="font-display text-xl tracking-tight">
              Tea<span className="text-tea-accent">L;DR</span>
            </span>
          </Link>
          
          <div className="flex items-center gap-8">
            <Link href="/#commands" className="text-sm font-medium hover:text-tea-accent transition-colors">
              Commands
            </Link>
            <Link href="/terms" className="text-sm font-medium hover:text-tea-accent transition-colors">
              Terms
            </Link>
            <Link href="/privacy" className="text-sm font-medium hover:text-tea-accent transition-colors">
              Privacy
            </Link>
            <a 
              href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2 bg-gradient-to-r from-tea-accent to-tea-green text-tea-darker font-medium rounded-lg hover:shadow-lg hover:shadow-tea-accent/50 transition-all hover:scale-105"
            >
              Add to Discord
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
