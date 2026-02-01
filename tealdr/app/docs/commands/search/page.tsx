import Link from 'next/link';

export default function SearchCommands() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a] border-b border-[#5865F2]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight">teal;dr</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/" className="text-[#a0a0a0] hover:text-[#5865F2] transition-colors duration-200">
              HOME
            </Link>
            <Link href="/docs" className="text-[#5865F2] font-bold">
              DOCS
            </Link>
          </div>
        </div>
      </header>

      <div className="flex pt-16">
        <aside className="hidden lg:block w-64 fixed left-0 top-16 bottom-0 border-r border-[#1a1a1a] overflow-y-auto">
          <nav className="p-6 space-y-8">
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Getting Started</h3>
              <ul className="space-y-2">
                <li><Link href="/docs" className="text-gray-400 hover:text-white transition-colors">Introduction</Link></li>
                <li><Link href="/docs/installation" className="text-gray-400 hover:text-white transition-colors">Installation</Link></li>
                <li><Link href="/docs/quickstart" className="text-gray-400 hover:text-white transition-colors">Quick Start</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Commands</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/commands/search" className="text-[#5865F2] hover:text-white transition-colors">Search Commands</Link></li>
                <li><Link href="/docs/commands/analytics" className="text-gray-400 hover:text-white transition-colors">Analytics</Link></li>
                <li><Link href="/docs/commands/utility" className="text-gray-400 hover:text-white transition-colors">Utility</Link></li>
                <li><Link href="/docs/commands/admin" className="text-gray-400 hover:text-white transition-colors">Admin</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Configuration</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/config/settings" className="text-gray-400 hover:text-white transition-colors">Bot Settings</Link></li>
                <li><Link href="/docs/config/permissions" className="text-gray-400 hover:text-white transition-colors">Permissions</Link></li>
                <li><Link href="/docs/config/retention" className="text-gray-400 hover:text-white transition-colors">Data Retention</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Advanced</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/advanced/api" className="text-gray-400 hover:text-white transition-colors">API Reference</Link></li>
                <li><Link href="/docs/advanced/architecture" className="text-gray-400 hover:text-white transition-colors">Architecture</Link></li>
                <li><Link href="/docs/advanced/troubleshooting" className="text-gray-400 hover:text-white transition-colors">Troubleshooting</Link></li>
              </ul>
            </div>
          </nav>
        </aside>

        <main className="flex-1 lg:ml-64 px-6 py-12 max-w-4xl">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">Search Commands</h1>
            <p className="text-xl text-gray-400">
              Comprehensive guide to TeaL;DR&apos;s semantic search capabilities.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/ask</h2>
              <p className="text-gray-300 mb-4">
                The primary search command. Uses natural language processing to find relevant messages based on semantic meaning rather than exact keyword matches.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /ask query: &lt;your search query&gt; [channel: #channel] [user: @user] [limit: number]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">query</strong> (required): Natural language search query</li>
                  <li><strong className="text-white">channel</strong> (optional): Limit search to specific channel</li>
                  <li><strong className="text-white">user</strong> (optional): Limit search to specific user&apos;s messages</li>
                  <li><strong className="text-white">limit</strong> (optional): Number of results to return (default: 5, max: 20)</li>
                </ul>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Examples</h3>
                
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Basic search:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /ask query: deployment issues last week
                  </code>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Search in specific channel:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /ask query: API documentation channel: #dev-team
                  </code>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Search specific user&apos;s messages:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /ask query: bug reports user: @john limit: 10
                  </code>
                </div>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg mb-6">
                <h4 className="text-sm font-semibold mb-2">💡 Pro Tips</h4>
                <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                  <li>Use descriptive phrases instead of single keywords for better results</li>
                  <li>The bot understands context - &quot;what did we decide about the API?&quot; works better than &quot;API decision&quot;</li>
                  <li>Follow-up questions maintain context from previous searches</li>
                  <li>Results are ranked by relevance, not chronological order</li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/recap</h2>
              <p className="text-gray-300 mb-4">
                Generate AI-powered summaries of conversations over a specified time period. Useful for catching up on missed discussions or reviewing past conversations.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /recap period: &lt;time period&gt; [channel: #channel] [format: brief|detailed]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">period</strong> (required): Time period to summarize (Last 24 hours, Last 7 days, Last 30 days, Custom)</li>
                  <li><strong className="text-white">channel</strong> (optional): Limit recap to specific channel</li>
                  <li><strong className="text-white">format</strong> (optional): Summary format - brief (key points) or detailed (comprehensive)</li>
                </ul>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Examples</h3>
                
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Daily recap:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /recap period: Last 24 hours format: brief
                  </code>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Weekly channel summary:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /recap period: Last 7 days channel: #general format: detailed
                  </code>
                </div>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Recap Output Includes</h3>
                <ul className="list-disc list-inside text-gray-300 space-y-2">
                  <li>Main topics discussed</li>
                  <li>Key decisions made</li>
                  <li>Action items mentioned</li>
                  <li>Most active participants</li>
                  <li>Important links or resources shared</li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/timemachine</h2>
              <p className="text-gray-300 mb-4">
                View what happened on a specific date in previous years. Great for anniversaries, recurring events, or historical context.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /timemachine date: &lt;MM-DD&gt; [channel: #channel]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">date</strong> (required): Date in MM-DD format (e.g., 01-31)</li>
                  <li><strong className="text-white">channel</strong> (optional): Limit results to specific channel</li>
                </ul>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Examples</h3>
                
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">View today&apos;s history:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /timemachine date: 01-31
                  </code>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Channel-specific history:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /timemachine date: 12-25 channel: #announcements
                  </code>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Search Best Practices</h2>
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Use Natural Language</h3>
                  <p className="text-gray-300 mb-2">
                    TeaL;DR understands context and meaning. Write queries as you would ask a person.
                  </p>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">❌ Less effective:</p>
                      <code className="text-xs text-gray-400">bug fix</code>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">✅ More effective:</p>
                      <code className="text-xs text-[#5865F2]">what bugs were fixed last week?</code>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Be Specific</h3>
                  <p className="text-gray-300 mb-2">
                    Include relevant details to narrow down results.
                  </p>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">❌ Too vague:</p>
                      <code className="text-xs text-gray-400">meeting</code>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">✅ More specific:</p>
                      <code className="text-xs text-[#5865F2]">sprint planning meeting decisions</code>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Use Filters</h3>
                  <p className="text-gray-300">
                    Combine query with channel and user filters to quickly find what you need in large servers.
                  </p>
                </div>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/installation" className="text-[#5865F2] hover:underline">
                ← Installation
              </Link>
              <Link href="/docs/commands/analytics" className="text-[#5865F2] hover:underline">
                Analytics Commands →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
