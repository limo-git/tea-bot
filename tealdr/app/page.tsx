'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { GLSLHills } from './components/glsl-hills';
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
    { name: '/lookup', desc: 'Exact message search' },
    { name: '/recap', desc: 'AI conversation summaries' },
    { name: '/private_session', desc: 'Temporary indexing control (Admin)' },
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

      {/* HERO SECTION - GLSL Hills Background */}
      <section className="relative h-screen overflow-hidden">
        {/* Animated GLSL Background */}
        <div className="absolute inset-0 z-0">
          <GLSLHills width="100vw" height="100vh" cameraZ={125} planeSize={256} speed={0.5} />
        </div>
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 z-10 bg-gradient-to-b from-[#0a0a0a]/80 via-[#0a0a0a]/60 to-[#0a0a0a]" />
        
        {/* Hero Content */}
        <div className="relative z-20 h-full flex items-center justify-center px-4 sm:px-6">
          <div className="max-w-7xl mx-auto text-center w-full">
            <div className="mb-6 sm:mb-8">
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-black mb-4 sm:mb-6 leading-tight px-2" style={{ letterSpacing: '-0.02em' }}>
                You know the conversation happened.
                <br />
                <span className="text-[#5865F2]">You just can't find it.</span>
              </h1>
              <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-[#c0c0c0] mb-8 sm:mb-12 max-w-3xl mx-auto leading-relaxed px-2">
                Ctrl + F for your Discord server
                <br className="hidden sm:block" />
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-4">
              <a
                href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto px-8 sm:px-10 py-3 sm:py-4 bg-[#5865F2] text-white font-bold text-base sm:text-lg border-2 border-[#5865F2] transition-all duration-200 hover:scale-105"
                onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 0 40px rgba(88, 101, 242, 0.6)'}
                onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
              >
                ADD TO DISCORD
              </a>
              <Link
                href="/docs"
                className="w-full sm:w-auto px-8 sm:px-10 py-3 sm:py-4 border-2 border-[#5865F2] text-[#5865F2] font-bold text-base sm:text-lg hover:bg-[#5865F2] hover:text-white transition-all duration-200"
              >
                VIEW DOCS
              </Link>
            </div>
            
            {/* Stats */}
            <div className="mt-8 sm:mt-12 md:mt-16 grid grid-cols-3 gap-3 sm:gap-6 md:gap-8 max-w-2xl mx-auto px-4">
              <div className="text-center">
                <div className="text-2xl sm:text-3xl md:text-4xl font-black text-[#5865F2] mb-1 sm:mb-2">7</div>
                <div className="text-xs sm:text-sm text-[#a0a0a0] leading-tight">Retrieval Pipelines</div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl md:text-4xl font-black text-[#5865F2] mb-1 sm:mb-2">Hybrid</div>
                <div className="text-xs sm:text-sm text-[#a0a0a0] leading-tight">BM25 + Vectors</div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl md:text-4xl font-black text-[#5865F2] mb-1 sm:mb-2">0</div>
                <div className="text-xs sm:text-sm text-[#a0a0a0] leading-tight">Hallucinations</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20 animate-bounce">
          <div className="w-6 h-10 border-2 border-[#5865F2]/50 rounded-full flex items-start justify-center p-2">
            <div className="w-1 h-3 bg-[#5865F2] rounded-full" />
          </div>
        </div>
      </section>

      {/* THE PROBLEM SECTION */}
      <section className="py-20 px-6 bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              Discord search is <span className="text-[#5865F2]">broken</span>.
            </h2>
            <p className="text-xl text-[#c0c0c0] leading-relaxed mb-6">
              Not technically — it works fine. But try finding a message when you don't remember the exact words, or who said it, or when.
            </p>
            <p className="text-xl text-[#c0c0c0] leading-relaxed mb-6">
              You're just... <span className="text-[#5865F2]">scrolling. Forever.</span>
            </p>
            <p className="text-xl text-[#c0c0c0] leading-relaxed">
              That's what TeaL;DR solves.
            </p>
          </div>
        </div>
      </section>

      {/* THE SOLUTION - TECHNICAL DEEP DIVE */}
      {/* <section className="py-20 px-6 bg-[#1a1a1a]">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              I'll be honest, I went a bit <span className="text-[#5865F2]">overboard</span> with the architecture.
            </h2>
          </div>

          <div className="space-y-8 text-lg text-[#c0c0c0] leading-relaxed">
            <p>
              It runs <strong className="text-white">7 different retrieval pipelines</strong> depending on what you're actually asking.
            </p>
            
            <div className="bg-[#0a0a0a] border-l-4 border-[#5865F2] p-6">
              <p className="mb-4">
                A simple lookup uses <strong className="text-[#5865F2]">hybrid search</strong> — BM25 for keywords, dense vectors for meaning, 
                fused together with Reciprocal Rank Fusion so neither one misses what the other would catch.
              </p>
              <p className="mb-4">
                A "who knows about X" question traverses a <strong className="text-[#5865F2]">Neo4j knowledge graph</strong> instead.
              </p>
              <p>
                A recap pulls from <strong className="text-[#5865F2]">pre-summarized hourly chunks</strong> so it's actually fast.
              </p>
            </div>

            <p>
              And it <strong className="text-white">doesn't hallucinate</strong>. There's a confidence layer that rejects weak results, 
              and if the first search pass wasn't good enough, it re-searches with a smarter query before responding.
            </p>
            
            <p className="text-[#a0a0a0] italic">
              I got tired of AI tools making things up, so I made sure this one just says "I don't know" when it doesn't.
            </p>
          </div>
        </div>
      </section> */}

      {/* KEY COMMANDS */}
      <section className="py-20 px-6 bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <p className="text-[#5865F2] text-sm mb-2">// CTRL+F FOR YOUR DISCORD SERVER</p>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              Key Commands
            </h2>
          </div>

          <div className="space-y-6">
            <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/30 p-6 hover:border-[#5865F2] transition-colors">
              <div className="flex items-start gap-4">
                <code className="text-[#5865F2] font-bold text-lg">/ask</code>
                <div>
                  <p className="text-white mb-2">Ask the bot about anyone and anything</p>
                  <p className="text-sm text-[#a0a0a0]">Natural language queries that actually understand context</p>
                </div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/30 p-6 hover:border-[#5865F2] transition-colors">
              <div className="flex items-start gap-4">
                <code className="text-[#5865F2] font-bold text-lg">/lookup</code>
                <div>
                  <p className="text-white mb-2">Give clues to find the exact text you were looking for</p>
                  <p className="text-sm text-[#a0a0a0]">Hybrid BM25 + vector search for precision</p>
                </div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/30 p-6 hover:border-[#5865F2] transition-colors">
              <div className="flex items-start gap-4">
                <code className="text-[#5865F2] font-bold text-lg">/recap</code>
                <div>
                  <p className="text-white mb-2">Summarize based on a time period</p>
                  <p className="text-sm text-[#a0a0a0]">Set it up for daily DMs if you want to stay updated without reading everything</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOR THE NERDS */}
      <section className="py-20 px-6 bg-[#1a1a1a]">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <p className="text-[#5865F2] text-sm mb-2 font-mono">// FOR THE NERDS</p>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              Technical Details
            </h2>
          </div>

          <div className="bg-[#0a0a0a] border-2 border-[#5865F2]/30 p-8 font-mono text-sm">
            <div className="space-y-4 text-[#c0c0c0]">
              <div>
                <span className="text-[#5865F2]">→</span> <strong className="text-white">BM25 keyword matching</strong> + dense vector semantic search
                <br />
                <span className="ml-4 text-[#a0a0a0]">Both exact keywords and semantics matter. Fused with RRF.</span>
              </div>
              
              <div>
                <span className="text-[#5865F2]">→</span> <strong className="text-white">7 different retrieval pipelines</strong>
                <br />
                <span className="ml-4 text-[#a0a0a0]">Simple lookup hits hybrid search, "who knows X" traverses Neo4j graph via Cypher</span>
              </div>
              
              <div>
                <span className="text-[#5865F2]">→</span> <strong className="text-white">Confidence gating layer</strong>
                <br />
                <span className="ml-4 text-[#a0a0a0]">Rejects weak retrieval results. No hallucinations.</span>
              </div>
              
              <div>
                <span className="text-[#5865F2]">→</span> <strong className="text-white">Corrective RAG loop</strong>
                <br />
                <span className="ml-4 text-[#a0a0a0]">Re-searches with refined query if first pass wasn't good enough</span>
              </div>
              
              <div className="pt-4 border-t border-[#5865F2]/30">
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* VIDEO DEMO SECTION */}
      <section className="py-20 px-6 bg-[#0a0a0a]">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <p className="text-[#5865F2] text-sm mb-2">// SEE IT IN ACTION</p>
            <h2 className="text-4xl md:text-5xl font-black mb-6">
              Watch How It Works
            </h2>
            <p className="text-lg text-[#c0c0c0]">
              Real demonstration of TeaL;DR in action — searching, finding, and delivering results instantly.
            </p>
          </div>

          <div className="relative bg-[#1a1a1a] border-2 border-[#5865F2]/30 p-4 sm:p-6 md:p-8">
            <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-[#0a0a0a]">
              <video
                className="w-full h-full object-contain"
                controls
                preload="metadata"
              >
                <source src="/work10.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
            
            <div className="mt-6 grid sm:grid-cols-3 gap-4 text-center">
              <div className="bg-[#0a0a0a] border border-[#5865F2]/20 p-4">
                <div className="text-[#5865F2] font-bold mb-1">Natural Language</div>
                <div className="text-xs text-[#a0a0a0]">Ask questions like you would to a human</div>
              </div>
              <div className="bg-[#0a0a0a] border border-[#5865F2]/20 p-4">
                <div className="text-[#5865F2] font-bold mb-1">Instant Results</div>
                <div className="text-xs text-[#a0a0a0]">Get answers in milliseconds</div>
              </div>
              <div className="bg-[#0a0a0a] border border-[#5865F2]/20 p-4">
                <div className="text-[#5865F2] font-bold mb-1">Source Citations</div>
                <div className="text-xs text-[#a0a0a0]">Every answer backed by actual messages</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* REMOVED OLD NEW FEATURES SHOWCASE */}
      <section className="py-20 px-6 bg-[#1a1a1a] hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/50 p-8 relative overflow-hidden group">
              <div className="mb-6">
                <div className="text-4xl mb-4">◀️ ▶️</div>
                <h3 className="text-3xl font-black mb-4 text-[#5865F2]">Pagination Controls</h3>
                <p className="text-[#a0a0a0] leading-relaxed mb-6">
                  Navigate through long responses with arrow buttons. Both <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/ask</code> and <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/lookup</code> now feature:
                </p>
                <ul className="space-y-2 text-[#c0c0c0]">
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Arrow buttons for page navigation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Toggle between results and sources</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Thumbs up/down feedback buttons</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Smart page splitting (1800 chars/page)</span>
                  </li>
                </ul>
              </div>
              <div className="bg-[#0a0a0a] border border-[#5865F2]/30 p-4 font-mono text-xs">
                <div className="text-[#5865F2] mb-2">Example:</div>
                <div className="text-[#a0a0a0]">
                  [◀️] [▶️] [📊 Show Sources] [👍] [👎]
                  <br />
                  Page 1/3 • 10 sources used
                </div>
              </div>
            </div>

            {/* Private Sessions Feature */}
            <div className="bg-[#1a1a1a] border-2 border-[#5865F2]/50 p-8 relative overflow-hidden group">
              <div className="absolute top-4 right-4 px-3 py-1 bg-[#5865F2] text-white text-xs font-bold">
                NEW
              </div>
              <div className="mb-6">
                <div className="text-4xl mb-4">🔒</div>
                <h3 className="text-3xl font-black mb-4 text-[#5865F2]">Private Sessions</h3>
                <p className="text-[#a0a0a0] leading-relaxed mb-6">
                  Admins can temporarily disable message indexing for sensitive discussions. Perfect for:
                </p>
                <ul className="space-y-2 text-[#c0c0c0]">
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Executive meetings & private discussions</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Auto-expiry after set duration</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Manual override to stop early</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Per-channel control</span>
                  </li>
                </ul>
              </div>
              <div className="bg-[#0a0a0a] border border-[#5865F2]/30 p-4 font-mono text-xs">
                <div className="text-[#5865F2] mb-2">Usage:</div>
                <div className="text-[#a0a0a0]">
                  /private_session action:Start
                  <br />
                  channel:#executive duration:60
                </div>
              </div>
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

          {/* All 18 Commands Grid */}
          <div>
            <p className="text-[#a0a0a0] text-sm mb-6">ALL 18 COMMANDS AVAILABLE:</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {commands.map((cmd, idx) => (
                <div 
                  key={idx}
                  className="relative p-3 bg-[#0a0a0a] border border-[#5865F2]/30 hover:border-[#5865F2] transition-all duration-200"
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
