'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Home() {
  const [activeTab, setActiveTab] = useState('ask');
  const [typedText, setTypedText] = useState('');
  const [isScrolled, setIsScrolled] = useState(false);
  const fullText = 'Transform Discord conversations into searchable knowledge';

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 50);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      title: 'AI Search',
      description: 'Semantic search that understands context and meaning, not just keywords'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      title: 'Message Recap',
      description: 'AI-generated summaries of conversations over any time period'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Smart Indexing',
      description: 'Automatic message indexing with intelligent caching for instant results'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
      title: 'Real-time Updates',
      description: 'Messages are indexed in real-time as they are sent in your server'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: 'Server Analytics',
      description: 'Comprehensive statistics and insights about server activity'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
      title: 'Auto-Organization',
      description: 'Automatic tagging and categorization of messages for better organization'
    }
  ];

  const commandTabs = {
    ask: {
      title: '/ask',
      description: 'Search through your server history with natural language',
      example: '/ask query: what did @john say about the API yesterday?',
      response: 'Found 3 relevant messages from @john about the API:\n\n1. "The new API endpoint is working great!"\n2. "We should update the documentation"\n3. "Rate limiting is set to 100 req/min"'
    },
    recap: {
      title: '/recap',
      description: 'Get AI-generated summaries of conversations',
      example: '/recap period: Last 7 days channel: #general',
      response: 'Summary of #general (Last 7 days):\n\nMain topics discussed:\n• New feature deployment\n• Bug fixes in authentication\n• Team meeting scheduled for Friday\n\nMost active members: @alice, @bob, @charlie'
    },
    stats: {
      title: '/stats',
      description: 'View comprehensive server and user activity statistics',
      example: '/stats scope: Server Statistics',
      response: 'Server Statistics:\n\n📊 Total Messages: 15,234\n👥 Active Users: 87\n📝 Most Active Channel: #general (3,421 messages)\n⏰ Peak Activity: 2-4 PM UTC\n🔥 Trending Topics: API, deployment, testing'
    },
    export: {
      title: '/export',
      description: 'Export search results to various formats',
      example: '/export query: project discussions format: CSV',
      response: 'Export completed successfully!\n\n📁 File: project_discussions.csv\n📊 Records: 156 messages\n💾 Size: 42 KB\n\nDownload link expires in 24 hours.'
    },
    quiz: {
      title: '/quiz',
      description: 'Create a Kahoot-style trivia game from server history',
      example: '/quiz num_questions: 5 time_period: Last 30 days',
      response: 'Quiz created! 🎮\n\nQuestions: 5\nTime per question: 30 seconds\nCategory: Server History\n\nStarting in 10 seconds...\nReact with 🎯 to join!'
    },
    wrapped: {
      title: '/wrapped',
      description: 'Generate a Spotify Wrapped-style yearly summary',
      example: '/wrapped year: 2025',
      response: '🎊 Your 2025 Wrapped!\n\nTop Contributor: @alice (2,341 messages)\nMost Active Month: March\nFavorite Channel: #general\nTop Topics: coding, design, meetings\n\nYou sent 15,234 messages this year! 🚀'
    },
    timemachine: {
      title: '/timemachine',
      description: 'See what happened on this day in previous years',
      example: '/timemachine date: 01-31',
      response: '⏰ On This Day (January 31):\n\n2024: Project launch announcement\n2023: Team celebration for 1000 members\n2022: First bot integration\n\n3 years of memories! 🎉'
    },
    settings: {
      title: '/settings',
      description: 'Configure bot behavior and permissions (Admin only)',
      example: '/settings action: Exclude Channel channel: #private',
      response: 'Settings updated successfully!\n\n✓ Channel #private excluded from indexing\n✓ Existing messages will not be searchable\n✓ New messages will be ignored'
    },
    customize: {
      title: '/customize',
      description: 'Set custom bot personality (Admin only)',
      example: '/customize persona: Professional',
      response: 'Bot personality updated! 🎨\n\nNew persona: Professional\nTone: Formal and concise\nResponse style: Business-focused\n\nThe bot will now respond with a professional tone.'
    },
    clear: {
      title: '/clear',
      description: 'Clear your conversation context with the bot',
      example: '/clear',
      response: 'Conversation context cleared! 🗑️\n\nYour chat history with the bot has been reset.\nStart fresh with a new conversation.'
    },
    help: {
      title: '/help',
      description: 'Show all available commands and usage tips',
      example: '/help',
      response: 'TeaL;DR Command Reference 📚\n\nSearch: /ask, /recap, /timemachine\nAnalytics: /stats\nUtility: /export, /clear, /help\nFun: /quiz, /wrapped\nAdmin: /settings, /customize\n\nUse /help [command] for detailed info!'
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <header 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? 'bg-[#0a0a0a]/95 backdrop-blur-md border-b border-[#5865F2]/20' : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center font-bold text-lg shadow-lg shadow-[#5865F2]/50">
              T
            </div>
            <span className="text-xl font-bold">TeaL;DR</span>
          </div>
          
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-400 hover:text-white transition-colors duration-300">Features</a>
            <a href="#commands" className="text-gray-400 hover:text-white transition-colors duration-300">Commands</a>
            <Link href="/docs" className="text-gray-400 hover:text-white transition-colors duration-300">Docs</Link>
            <a href="#cta" className="text-gray-400 hover:text-white transition-colors duration-300">Get Started</a>
          </nav>
          
          <a
            href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 bg-[#5865F2] rounded-lg font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-[#5865F2]/50 hover:scale-105"
          >
            Add to Discord
          </a>
        </div>
      </header>

      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'linear-gradient(#5865F2 1px, transparent 1px), linear-gradient(90deg, #5865F2 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }}></div>
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-12 py-28">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              {typedText}<span className="animate-pulse">|</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 mb-8 max-w-3xl mx-auto">
              TeaL;DR brings powerful AI-driven semantic search to your Discord server. Never lose track of important conversations again.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <a
                href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
                target="_blank"
                rel="noopener noreferrer"
                className="px-8 py-4 bg-[#5865F2] rounded-xl font-bold text-lg transition-all duration-300 hover:shadow-xl hover:shadow-[#5865F2]/50 hover:scale-105"
              >
                Add Bot to Server
              </a>
              <a
                href="#commands"
                className="px-8 py-4 border-2 border-[#5865F2] rounded-xl font-bold text-lg transition-all duration-300 hover:bg-[#5865F2]/10 hover:scale-105"
              >
                View Documentation
              </a>
            </div>

            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div>
                <div className="text-3xl font-bold text-[#5865F2] mb-1">1000+</div>
                <div className="text-sm text-gray-500">Servers</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-[#5865F2] mb-1">50K+</div>
                <div className="text-sm text-gray-500">Messages Indexed</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-[#5865F2] mb-1">99.9%</div>
                <div className="text-sm text-gray-500">Uptime</div>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute top-20 left-10 w-64 h-64 bg-[#5865F2]/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-80 h-80 bg-[#5865F2]/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </section>

      <section id="features" className="py-20 px-6 bg-[#0a0a0a]/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-400">Everything you need to unlock your server&apos;s knowledge</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20 hover:scale-105 cursor-pointer"
              >
                <div className="text-[#5865F2] mb-4 transition-transform duration-300 group-hover:scale-110">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-6 bg-[#0a0a0a]/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">All Commands</h2>
            <p className="text-xl text-gray-400">11 powerful slash commands at your fingertips</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">🔍</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/ask</h3>
              </div>
              <p className="text-gray-400 mb-3">Natural language search through your server history</p>
              <code className="text-xs text-gray-500 font-mono">query: what did @user say about the API?</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">📝</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/recap</h3>
              </div>
              <p className="text-gray-400 mb-3">AI-generated summaries of conversations over time</p>
              <code className="text-xs text-gray-500 font-mono">period: Last 7 days</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">📊</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/stats</h3>
              </div>
              <p className="text-gray-400 mb-3">View server and user activity statistics</p>
              <code className="text-xs text-gray-500 font-mono">scope: Server Statistics</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">📤</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/export</h3>
              </div>
              <p className="text-gray-400 mb-3">Export search results to JSON, CSV, Markdown, or TXT</p>
              <code className="text-xs text-gray-500 font-mono">format: CSV</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">🎮</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/quiz</h3>
              </div>
              <p className="text-gray-400 mb-3">Kahoot-style trivia game from server history</p>
              <code className="text-xs text-gray-500 font-mono">num_questions: 5</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">🎊</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/wrapped</h3>
              </div>
              <p className="text-gray-400 mb-3">Spotify Wrapped-style yearly server summary</p>
              <code className="text-xs text-gray-500 font-mono">year: 2025</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">⏰</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/timemachine</h3>
              </div>
              <p className="text-gray-400 mb-3">See what happened on this day in previous years</p>
              <code className="text-xs text-gray-500 font-mono">date: 01-31</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">⚙️</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/settings</h3>
              </div>
              <p className="text-gray-400 mb-3">Configure bot settings (Admin only)</p>
              <code className="text-xs text-gray-500 font-mono">action: Exclude Channel</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">🎨</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/customize</h3>
              </div>
              <p className="text-gray-400 mb-3">Set custom bot personality (Admin only)</p>
              <code className="text-xs text-gray-500 font-mono">persona: Professional</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">🗑️</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/clear</h3>
              </div>
              <p className="text-gray-400 mb-3">Clear your conversation context with the bot</p>
              <code className="text-xs text-gray-500 font-mono">/clear</code>
            </div>

            <div className="group p-6 bg-[#111111] border border-[#1a1a1a] rounded-2xl transition-all duration-300 hover:border-[#5865F2] hover:shadow-lg hover:shadow-[#5865F2]/20">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-2xl">❓</div>
                <h3 className="text-xl font-bold text-[#5865F2]">/help</h3>
              </div>
              <p className="text-gray-400 mb-3">Show all available commands and tips</p>
              <code className="text-xs text-gray-500 font-mono">/help</code>
            </div>
          </div>
        </div>
      </section>

      <section id="commands" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Command Showcase</h2>
            <p className="text-xl text-gray-400">See TeaL;DR in action</p>
          </div>

          <div className="flex justify-center gap-4 mb-8">
            {Object.keys(commandTabs).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                  activeTab === tab
                    ? 'bg-[#5865F2] shadow-lg shadow-[#5865F2]/50'
                    : 'bg-[#111111] hover:bg-[#1a1a1a]'
                }`}
              >
                {commandTabs[tab as keyof typeof commandTabs].title}
              </button>
            ))}
          </div>

          <div className="bg-[#111111] border border-[#1a1a1a] rounded-2xl p-8">
            <h3 className="text-2xl font-bold mb-2">{commandTabs[activeTab as keyof typeof commandTabs].title}</h3>
            <p className="text-gray-400 mb-6">{commandTabs[activeTab as keyof typeof commandTabs].description}</p>
            
            <div className="space-y-4">
              <div className="bg-[#0a0a0a] border border-[#5865F2]/30 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-2">Example:</div>
                <code className="text-[#5865F2]">{commandTabs[activeTab as keyof typeof commandTabs].example}</code>
              </div>
              
              <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-2">Response:</div>
                <pre className="text-gray-300 whitespace-pre-wrap font-mono text-sm">{commandTabs[activeTab as keyof typeof commandTabs].response}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="cta" className="py-20 px-6 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#5865F2]/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#5865F2]/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1.5s' }}></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of servers using TeaL;DR to unlock their conversation history
          </p>
          
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-6">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="text-lg font-bold mb-2">Instant Setup</h3>
              <p className="text-gray-400">Add the bot and start searching in under 60 seconds</p>
            </div>
            <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-6">
              <div className="text-3xl mb-3">🔒</div>
              <h3 className="text-lg font-bold mb-2">Privacy First</h3>
              <p className="text-gray-400">Complete data isolation between servers</p>
            </div>
            <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-6">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="text-lg font-bold mb-2">Accurate Results</h3>
              <p className="text-gray-400">AI-powered semantic search understands context</p>
            </div>
            <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-6">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-bold mb-2">Rich Analytics</h3>
              <p className="text-gray-400">Comprehensive insights about server activity</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
              className="px-10 py-4 bg-[#5865F2] rounded-xl font-bold text-lg transition-all duration-300 hover:shadow-xl hover:shadow-[#5865F2]/50 hover:scale-105"
            >
              Add to Discord Now
            </a>
            <Link
              href="/terms"
              className="px-10 py-4 border-2 border-[#5865F2] rounded-xl font-bold text-lg transition-all duration-300 hover:bg-[#5865F2]/10 hover:scale-105"
            >
              View Terms
            </Link>
          </div>
        </div>
      </section>

      <footer className="py-12 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center font-bold text-lg shadow-lg shadow-[#5865F2]/50">
                  T
                </div>
                <span className="text-xl font-bold">TeaL;DR</span>
              </div>
              <p className="text-gray-400 text-sm mb-4">
                Transform Discord conversations into searchable knowledge with AI-powered semantic search.
              </p>
              
              <div className="flex items-center gap-3">
                <a href="https://discord.gg/T8VTnDWSKp" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-[#111111] border border-[#1a1a1a] rounded-lg flex items-center justify-center hover:border-[#5865F2] hover:bg-[#5865F2]/10 transition-all duration-300 group">
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-[#5865F2] transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
                  </svg>
                </a>
                <a href="https://x.com/limo_ew" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-[#111111] border border-[#1a1a1a] rounded-lg flex items-center justify-center hover:border-[#5865F2] hover:bg-[#5865F2]/10 transition-all duration-300 group">
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-[#5865F2] transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                </a>
                <a href="https://github.com/limo-git/tea-bot" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-[#111111] border border-[#1a1a1a] rounded-lg flex items-center justify-center hover:border-[#5865F2] hover:bg-[#5865F2]/10 transition-all duration-300 group">
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-[#5865F2] transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#features" className="hover:text-white transition-colors duration-300">Features</a></li>
                <li><a href="#commands" className="hover:text-white transition-colors duration-300">Commands</a></li>
                <li><Link href="/docs" className="hover:text-white transition-colors duration-300">Documentation</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors duration-300">Terms</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors duration-300">Privacy</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="/docs/installation" className="hover:text-white transition-colors duration-300">Installation</Link></li>
                <li><Link href="/docs/commands/search" className="hover:text-white transition-colors duration-300">Commands</Link></li>
                <li><Link href="/docs/config/settings" className="hover:text-white transition-colors duration-300">Configuration</Link></li>
                <li><a href="mailto:support@tealdr.com" className="hover:text-white transition-colors duration-300">Support</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Support Development</h3>
              <p className="text-gray-400 text-sm mb-4">
                Help keep TeaL;DR running and support future development.
              </p>
              <a
                href="https://www.buymeacoffee.com/YOUR_USERNAME"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#FFDD00] text-black font-semibold rounded-lg hover:bg-[#FFED4E] transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-[#FFDD00]/50"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.216 6.415l-.132-.666c-.119-.598-.388-1.163-1.001-1.379-.197-.069-.42-.098-.57-.241-.152-.143-.196-.366-.231-.572-.065-.378-.125-.756-.192-1.133-.057-.325-.102-.69-.25-.987-.195-.4-.597-.634-.996-.788a5.723 5.723 0 00-.626-.194c-1-.263-2.05-.36-3.077-.416a25.834 25.834 0 00-3.7.062c-.915.083-1.88.184-2.75.5-.318.116-.646.256-.888.501-.297.302-.393.77-.177 1.146.154.267.415.456.692.58.36.162.737.284 1.123.366 1.075.238 2.189.331 3.287.37 1.218.05 2.437.01 3.65-.118.299-.033.598-.073.896-.119.352-.054.578-.513.474-.834-.124-.383-.457-.531-.834-.473-.466.074-.96.108-1.382.146-1.177.08-2.358.082-3.536.006a22.228 22.228 0 01-1.157-.107c-.086-.01-.18-.025-.258-.036-.243-.036-.484-.08-.724-.13-.111-.027-.111-.185 0-.212h.005c.277-.06.557-.108.838-.147h.002c.131-.009.263-.032.394-.048a25.076 25.076 0 013.426-.12c.674.019 1.347.067 2.017.144l.228.031c.267.04.533.088.798.145.392.085.895.113 1.07.542.055.137.08.288.111.431l.319 1.484a.237.237 0 01-.199.284h-.003c-.037.006-.075.01-.112.015a36.704 36.704 0 01-4.743.295 37.059 37.059 0 01-4.699-.304c-.14-.017-.293-.042-.417-.06-.326-.048-.649-.108-.973-.161-.393-.065-.768-.032-1.123.161-.29.16-.527.404-.675.701-.154.316-.199.66-.267 1-.069.34-.176.707-.135 1.056.087.753.613 1.365 1.37 1.502a39.69 39.69 0 0011.343.376.483.483 0 01.535.53l-.071.697-1.018 9.907c-.041.41-.047.832-.125 1.237-.122.637-.553 1.028-1.182 1.171-.577.131-1.165.2-1.756.205-.656.004-1.31-.025-1.966-.022-.699.004-1.556-.06-2.095-.58-.475-.458-.54-1.174-.605-1.793l-.731-7.013-.322-3.094c-.037-.351-.286-.695-.678-.678-.336.015-.718.3-.678.679l.228 2.185.949 9.112c.147 1.344 1.174 2.068 2.446 2.272.742.12 1.503.144 2.257.156.966.016 1.942.053 2.892-.122 1.408-.258 2.465-1.198 2.616-2.657.34-3.332.683-6.663 1.024-9.995l.215-2.087a.484.484 0 01.39-.426c.402-.078.787-.212 1.074-.518.455-.488.546-1.124.385-1.766zm-1.478.772c-.145.137-.363.201-.578.233-2.416.359-4.866.54-7.308.46-1.748-.06-3.477-.254-5.207-.498-.17-.024-.353-.055-.47-.18-.22-.236-.111-.71-.054-.995.052-.26.152-.609.463-.646.484-.057 1.046.148 1.526.22.577.088 1.156.159 1.737.212 2.48.226 5.002.19 7.472-.14.45-.06.899-.13 1.345-.21.399-.072.84-.206 1.08.206.166.281.188.657.162.974a.544.544 0 01-.169.364zm-6.159 3.9c-.862.37-1.84.788-3.109.788a5.884 5.884 0 01-1.569-.217l.877 9.004c.065.78.717 1.38 1.5 1.38 0 0 1.243.065 1.658.065.447 0 1.786-.065 1.786-.065.783 0 1.434-.6 1.499-1.38l.94-9.95a3.996 3.996 0 00-1.322-.238c-.826 0-1.491.284-2.26.613z"/>
                </svg>
                Buy Me a Coffee
              </a>
            </div>
          </div>
          
          <div className="pt-8 border-t border-[#1a1a1a] text-center text-sm text-gray-500">
            <p>© 2026 TeaL;DR. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
