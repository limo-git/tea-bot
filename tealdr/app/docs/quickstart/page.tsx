import Link from 'next/link';

export default function QuickStart() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/95 backdrop-blur-md border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#5865F2] flex items-center justify-center font-bold text-lg shadow-lg shadow-[#5865F2]/50">
              T
            </div>
            <span className="text-xl font-bold">TeaL;DR</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/" className="text-gray-400 hover:text-white transition-colors duration-300">
              Home
            </Link>
            <Link href="/docs" className="text-[#5865F2]">
              Docs
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
                <li><Link href="/docs/quickstart" className="text-[#5865F2] hover:text-white transition-colors">Quick Start</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Commands</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/commands/search" className="text-gray-400 hover:text-white transition-colors">Search Commands</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Quick Start Guide</h1>
            <p className="text-xl text-gray-400">
              Get up and running with TeaL;DR in 5 minutes.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Your First Search</h2>
              <p className="text-gray-300 mb-4">
                After installing TeaL;DR, try your first search to see the bot in action.
              </p>

              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Step 1: Wait for Indexing</h3>
                  <p className="text-gray-300 mb-3">
                    The bot needs a few minutes to index recent messages. For new installations, it will automatically index the last 1000 messages per channel.
                  </p>
                  <div className="p-3 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded text-sm text-gray-300">
                    <strong>Tip:</strong> You can check indexing status with <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/stats</code>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Step 2: Run Your First Query</h3>
                  <p className="text-gray-300 mb-3">
                    Use natural language to search for something discussed in your server:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                    /ask query: what did we discuss about the project deadline?
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Step 3: Review Results</h3>
                  <p className="text-gray-300 mb-3">
                    The bot will return relevant messages with context. Results include:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 space-y-1 text-sm">
                    <li>Message content and author</li>
                    <li>Channel and timestamp</li>
                    <li>Relevance score</li>
                    <li>Direct link to original message</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Essential Commands</h2>
              <p className="text-gray-300 mb-6">
                Master these five commands to get the most out of TeaL;DR:
              </p>

              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-center gap-3 mb-3">
                    <code className="text-[#5865F2] font-mono font-bold">/ask</code>
                    <span className="px-2 py-1 bg-[#5865F2]/20 text-[#5865F2] text-xs rounded">Most Used</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">
                    Search through your server history using natural language. This is your primary tool for finding information.
                  </p>
                  <code className="block text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /ask query: bug reports from last week
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-center gap-3 mb-3">
                    <code className="text-[#5865F2] font-mono font-bold">/recap</code>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">
                    Get AI-generated summaries of conversations. Perfect for catching up after being away.
                  </p>
                  <code className="block text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /recap period: Last 7 days
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-center gap-3 mb-3">
                    <code className="text-[#5865F2] font-mono font-bold">/stats</code>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">
                    View server analytics including message counts, active users, and trending topics.
                  </p>
                  <code className="block text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /stats scope: Server Statistics
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-center gap-3 mb-3">
                    <code className="text-[#5865F2] font-mono font-bold">/export</code>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">
                    Export search results to CSV, JSON, or Markdown for external analysis.
                  </p>
                  <code className="block text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /export query: meeting notes format: CSV
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-center gap-3 mb-3">
                    <code className="text-[#5865F2] font-mono font-bold">/settings</code>
                    <span className="px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded">Admin Only</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">
                    Configure bot behavior, exclude channels, and manage data retention.
                  </p>
                  <code className="block text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: Exclude Channel channel: #private
                  </code>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Common Use Cases</h2>
              
              <div className="space-y-6">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold mb-3">Finding Past Decisions</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Quickly locate when and why decisions were made:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mb-2">
                    /ask query: why did we choose PostgreSQL over MongoDB?
                  </code>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /ask query: what was decided about the API versioning?
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold mb-3">Onboarding New Members</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Help new team members catch up on context:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mb-2">
                    /recap period: Last 30 days channel: #general
                  </code>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /ask query: project overview and current status
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold mb-3">Tracking Action Items</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Find tasks and follow-ups mentioned in conversations:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mb-2">
                    /ask query: action items from yesterday&apos;s meeting
                  </code>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /ask query: who was assigned to fix the login bug?
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold mb-3">Research and Analysis</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Export data for deeper analysis:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mb-2">
                    /export query: feature requests format: CSV
                  </code>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /stats scope: User Activity
                  </code>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Best Practices</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">✓ Do</h3>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>• Use descriptive, natural language queries</li>
                    <li>• Exclude sensitive channels from indexing</li>
                    <li>• Review retention settings for your needs</li>
                    <li>• Use channel filters for targeted searches</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-orange-400 mb-2">✗ Don&apos;t</h3>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>• Use single-word keyword searches</li>
                    <li>• Index channels with PII or sensitive data</li>
                    <li>• Spam commands (rate limits apply)</li>
                    <li>• Expect instant results on first install</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Next Steps</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <Link href="/docs/commands/search" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Advanced Search →</h3>
                  <p className="text-gray-400 text-sm">Learn advanced search techniques and filters</p>
                </Link>

                <Link href="/docs/config/settings" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Configuration →</h3>
                  <p className="text-gray-400 text-sm">Customize bot behavior for your server</p>
                </Link>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/installation" className="text-[#5865F2] hover:underline">
                ← Installation
              </Link>
              <Link href="/docs/commands/search" className="text-[#5865F2] hover:underline">
                Search Commands →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
