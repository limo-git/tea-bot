'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import InteractiveDemo from './components/InteractiveDemo';

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeCmd, setActiveCmd] = useState('ask');
  const [cursorBlink, setCursorBlink] = useState(true);
  const [typedFaster, setTypedFaster] = useState('');

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setCursorBlink(prev => !prev), 500);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const text = 'FASTER';
    let index = 0;
    const timer = setInterval(() => {
      if (index <= text.length) {
        setTypedFaster(text.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 150);
    return () => clearInterval(timer);
  }, []);

  const cmdOutputs: Record<string, string> = {
    ask: `$ tealdr /ask "what did @john say about the API?"
› Searching server history...
› Found 3 relevant messages in 18ms
› Top match: #dev-general (2 hours ago)

> "The new API endpoint is working great!"
> "We should update the documentation"
> "Rate limiting is set to 100 req/min"

› Search complete`,
    recap: `$ tealdr /recap period:"Last 7 days"
› Generating AI summary...
› Analyzed 1,247 messages
› Processing complete in 2.3s

> Main topics discussed:
> • New feature deployment
> • Bug fixes in authentication  
> • Team meeting scheduled

› Most active: @alice, @bob, @charlie`,
    search: `$ tealdr /search query:"react hooks"
› Semantic search initiated...
› Found 247 results across 12 channels
› Relevance score: 94%

> Top 3 matches:
> 1. #dev-general - "custom hooks pattern"
> 2. #help - "useEffect dependencies"
> 3. #code-review - "hooks best practices"

› Results ready`,
    tag: `$ tealdr /tag message:"important update"
› Auto-tagging enabled...
› Analyzing message content...
› Tags applied: #announcement #update

> Message categorized successfully
> Indexed under: announcements/2026
> Searchable: yes

› Tag operation complete`
  };

  const commands = [
    { name: '/ask', desc: 'Natural language search' },
    { name: '/recap', desc: 'AI conversation summaries' },
    { name: '/stats', desc: 'Server analytics' },
    { name: '/export', desc: 'Export to CSV/JSON/MD/TXT' },
    { name: '/quiz', desc: 'Trivia game from history' },
    { name: '/wrapped', desc: 'Yearly server summary' },
    { name: '/timemachine', desc: 'Historical events' },
    { name: '/settings', desc: 'Configure bot (Admin)' },
    { name: '/customize', desc: 'Bot personality (Admin)' },
    { name: '/clear', desc: 'Clear context' },
    { name: '/help', desc: 'Show all commands' },
    { name: '/request-summary', desc: 'DM/email summaries' },
    { name: '/bug-summary', desc: 'Bug discussions' },
    { name: '/dm-settings', desc: 'DM preferences' },
    { name: '/summary-topics', desc: 'Topic filtering' },
    { name: '/summary-servers', desc: 'Server selection' }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      {/* HEADER - Minimal Terminal */}
      <header 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
          isScrolled ? 'bg-[#0a0a0a] border-b border-[#5865F2]' : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight">TeaL;DR {cursorBlink ? '_' : ''}</span>
          </div>
          
          <a
            href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2 border-2 border-[#5865F2] text-[#5865F2] font-bold hover:bg-[#5865F2] hover:text-white transition-all duration-200"
            onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 20px rgba(88, 101, 242, 0.3)'}
            onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
          >
            INVITE
          </a>
        </div>
      </header>

      {/* HERO SECTION - Bold & Tilted */}
      <section className="relative pt-32 pb-20 my-32 px-6 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left - Typography */}
            <div style={{ transform: 'skewY(-2deg)' }}>
              <h1 className="text-8xl md:text-9xl font-black mb-4" style={{ letterSpacing: '-0.04em' }}>
                SEARCH
              </h1>
              <h1 className="text-8xl md:text-9xl font-black text-[#5865F2] mb-8" style={{ 
                letterSpacing: '-0.04em',
                textShadow: '0 0 40px rgba(88, 101, 242, 0.5)'
              }}>
                {typedFaster}<span className={cursorBlink ? 'opacity-100' : 'opacity-0'}>|</span>
              </h1>
              <p className="text-lg text-[#a0a0a0] mb-8 max-w-md" style={{ transform: 'skewY(2deg)' }}>
                Discord bot for semantic search. Find anything in your server history instantly.
              </p>
              <div className="flex gap-4" style={{ transform: 'skewY(2deg)' }}>
                <a
                  href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-8 py-3 bg-[#5865F2] text-white font-bold border-2 border-[#5865F2] transition-all duration-200"
                  onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 30px rgba(88, 101, 242, 0.5)'}
                  onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
                >
                  ADD NOW
                </a>
                <Link
                  href="/docs"
                  className="px-8 py-3 border-2 border-[#5865F2] text-[#5865F2] font-bold hover:bg-[#5865F2] hover:text-white transition-all duration-200"
                >
                  DOCS
                </Link>
              </div>
            </div>

            {/* Right - Terminal Output */}
            <div className="relative">
              <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/50 p-6">
                <div className="flex gap-2 mb-4">
                  <div className="w-3 h-3 border-2 border-[#5865F2]/40"></div>
                  <div className="w-3 h-3 border-2 border-[#5865F2]/40"></div>
                </div>
                <pre className="text-xs text-[#e0e0e0] leading-relaxed">
{`$ tealdr --search "server bugs"
› Found 12 results in 15ms
› Top match: #bug-reports (1 hour ago)
> "Database connection timeout on prod server"
› Summary: Critical bug affecting user authentication...`}
                </pre>
              </div>
              <div className="absolute -top-4 -right-4 w-6 h-6 border-2 border-[#5865F2]/40"></div>
              <div className="absolute -bottom-4 -left-4 w-6 h-6 border-2 border-[#5865F2]/40"></div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="py-20 px-6 bg-[#1a1a1a]">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16">
            <p className="text-[#5865F2] text-sm mb-2">// FEATURES</p>
            <h2 className="text-5xl md:text-6xl font-black">
              BUILT FOR <span className="text-[#5865F2]">POWER</span>
            </h2>
          </div>

          {/* Feature Cards Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            <div 
              className="group relative bg-[#0a0a0a] border-2 border-[#5865F2]/50 p-8 transition-all duration-300 hover:border-[#5865F2]"
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 40px rgba(88, 101, 242, 0.3)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
            >
              <div className="absolute top-4 right-4 text-6xl font-black text-[#5865F2]/10 group-hover:text-[#5865F2]/20 transition-colors">
                01
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 border-2 border-[#5865F2] mb-6 flex items-center justify-center">
                  <span className="text-2xl">🔍</span>
                </div>
                <h3 className="text-2xl font-black mb-4 text-[#5865F2]">AI SEARCH</h3>
                <p className="text-[#a0a0a0] leading-relaxed">
                  Semantic understanding of context and meaning, not just keywords. Find exactly what you need.
                </p>
              </div>
            </div>

            <div 
              className="group relative bg-[#0a0a0a] border-2 border-[#5865F2]/50 p-8 transition-all duration-300 hover:border-[#5865F2]"
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 40px rgba(88, 101, 242, 0.3)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
            >
              <div className="absolute top-4 right-4 text-6xl font-black text-[#5865F2]/10 group-hover:text-[#5865F2]/20 transition-colors">
                02
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 border-2 border-[#5865F2] mb-6 flex items-center justify-center">
                  <span className="text-2xl">⚡</span>
                </div>
                <h3 className="text-2xl font-black mb-4 text-[#5865F2]">REAL-TIME</h3>
                <p className="text-[#a0a0a0] leading-relaxed">
                  Instant indexing as messages are sent in your server. Zero lag, maximum efficiency.
                </p>
              </div>
            </div>

            <div 
              className="group relative bg-[#0a0a0a] border-2 border-[#5865F2]/50 p-8 transition-all duration-300 hover:border-[#5865F2]"
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 40px rgba(88, 101, 242, 0.3)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
            >
              <div className="absolute top-4 right-4 text-6xl font-black text-[#5865F2]/10 group-hover:text-[#5865F2]/20 transition-colors">
                03
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 border-2 border-[#5865F2] mb-6 flex items-center justify-center">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="text-2xl font-black mb-4 text-[#5865F2]">ANALYTICS</h3>
                <p className="text-[#a0a0a0] leading-relaxed">
                  Comprehensive server insights and activity statistics. Track everything that matters.
                </p>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-[#5865F2]/10 border-2 border-[#5865F2]/30 p-6" style={{ transform: 'rotate(-2deg)' }}>
              <div className="text-4xl font-black text-[#5865F2] mb-2">1000+</div>
              <div className="text-sm text-[#a0a0a0]">SERVERS</div>
            </div>
            <div className="bg-[#5865F2]/10 border-2 border-[#5865F2]/30 p-6" style={{ transform: 'rotate(2deg)' }}>
              <div className="text-4xl font-black text-[#5865F2] mb-2">50K+</div>
              <div className="text-sm text-[#a0a0a0]">MESSAGES</div>
            </div>
            <div className="bg-[#5865F2]/10 border-2 border-[#5865F2]/30 p-6" style={{ transform: 'rotate(-2deg)' }}>
              <div className="text-4xl font-black text-[#5865F2] mb-2">18MS</div>
              <div className="text-sm text-[#a0a0a0]">AVG SEARCH</div>
            </div>
            <div className="bg-[#5865F2]/10 border-2 border-[#5865F2]/30 p-6" style={{ transform: 'rotate(2deg)' }}>
              <div className="text-4xl font-black text-[#5865F2] mb-2">99.9%</div>
              <div className="text-sm text-[#a0a0a0]">UPTIME</div>
            </div>
          </div>
        </div>
      </section>

      {/* COMMANDS SECTION */}
      <section id="commands" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-[#5865F2] text-sm mb-2">// COMMANDS</p>
            <h2 className="text-5xl md:text-6xl font-black">
              TYPE & <span className="text-[#5865F2]">EXECUTE</span>
            </h2>
          </div>

          {/* All 16 Commands Grid */}
          <div>
            <p className="text-[#a0a0a0] text-sm mb-6">ALL 16 COMMANDS AVAILABLE:</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {commands.map((cmd, idx) => (
                <div 
                  key={idx}
                  className="p-3 bg-[#0a0a0a] border border-[#5865F2]/30 hover:border-[#5865F2] transition-all duration-200"
                  onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 20px rgba(88, 101, 242, 0.3)'}
                  onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
                >
                  <div className="text-sm font-bold text-[#5865F2] mb-1">{cmd.name}</div>
                  <div className="text-xs text-[#707070]">{cmd.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* INTERACTIVE DEMO SECTION */}
      <section className="py-20 px-6 bg-[#1a1a1a]">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-[#5865F2] text-sm mb-2">// INTERACTIVE</p>
            <h2 className="text-5xl md:text-6xl font-black">
              TRY IT <span className="text-[#5865F2]">LIVE</span>
            </h2>
          </div>
          <InteractiveDemo />
        </div>
      </section>

      {/* CTA SECTION - Bold Full-Width Block */}
      <section id="cta" className="py-20 px-6 bg-[#5865F2]/5 border-y-2 border-[#5865F2]/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left */}
            <div>
              <h2 className="text-7xl md:text-8xl font-black mb-6" style={{ letterSpacing: '-0.04em' }}>
                READY?
              </h2>
              <p className="text-lg text-[#a0a0a0] max-w-sm">
                Add TeaL;DR to your Discord server and unlock instant semantic search across your entire message history.
              </p>
            </div>

            {/* Right */}
            <div className="space-y-4">
              <a
                href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full px-8 py-4 bg-[#5865F2] text-white text-center font-bold border-2 border-[#5865F2] transition-all duration-200"
                onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 30px rgba(88, 101, 242, 0.5)'}
                onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
              >
                INVITE NOW
              </a>
              <Link
                href="/docs"
                className="block w-full px-8 py-4 border-2 border-[#5865F2] text-[#5865F2] text-center font-bold hover:bg-[#5865F2] hover:text-white transition-all duration-200"
              >
                DOCUMENTATION
              </Link>
              <p className="text-xs text-[#707070] text-center">Free forever • 30-day premium trial</p>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER - Minimal */}
      <footer className="py-12 px-6 bg-[#1a1a1a] border-t border-[#5865F2]/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-xl font-bold mb-4">TeaL;DR</div>
              <p className="text-sm text-[#a0a0a0] mb-4">
                Semantic search for Discord servers
              </p>
            </div>
            
            <div>
              <h3 className="font-bold mb-4 text-sm">PRODUCT</h3>
              <ul className="space-y-2 text-sm text-[#a0a0a0]">
                <li><a href="#features" className="hover:text-[#5865F2] transition-colors">Features</a></li>
                <li><a href="#commands" className="hover:text-[#5865F2] transition-colors">Commands</a></li>
                <li><Link href="/docs" className="hover:text-[#5865F2] transition-colors">Documentation</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4 text-sm">COMMUNITY</h3>
              <ul className="space-y-2 text-sm text-[#a0a0a0]">
                <li><a href="https://discord.gg/T8VTnDWSKp" target="_blank" rel="noopener noreferrer" className="hover:text-[#5865F2] transition-colors">Discord</a></li>
                <li><a href="https://x.com/limo_ew" target="_blank" rel="noopener noreferrer" className="hover:text-[#5865F2] transition-colors">X / Twitter</a></li>
                <li><a href="https://github.com/limo-git/tea-bot" target="_blank" rel="noopener noreferrer" className="hover:text-[#5865F2] transition-colors">GitHub</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4 text-sm">LEGAL</h3>
              <ul className="space-y-2 text-sm text-[#a0a0a0]">
                <li><Link href="/terms" className="hover:text-[#5865F2] transition-colors">Terms</Link></li>
                <li><Link href="/privacy" className="hover:text-[#5865F2] transition-colors">Privacy</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-[#5865F2]/30 text-center text-sm text-[#707070]">
            <p>© 2026 TeaL;DR. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
