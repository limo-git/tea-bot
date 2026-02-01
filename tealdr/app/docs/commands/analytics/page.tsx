import Link from 'next/link';

export default function AnalyticsCommands() {
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
                <li><Link href="/docs/commands/search" className="text-gray-400 hover:text-white transition-colors">Search Commands</Link></li>
                <li><Link href="/docs/commands/analytics" className="text-[#5865F2] hover:text-white transition-colors">Analytics</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Analytics Commands</h1>
            <p className="text-xl text-gray-400">
              Gain insights into server activity and user engagement.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/stats</h2>
              <p className="text-gray-300 mb-4">
                View comprehensive statistics about server activity, user engagement, and message patterns.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /stats scope: &lt;Server Statistics|User Activity|Channel Analytics&gt; [user: @user] [channel: #channel]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">scope</strong> (required): Type of statistics to display</li>
                  <li><strong className="text-white">user</strong> (optional): View stats for specific user</li>
                  <li><strong className="text-white">channel</strong> (optional): View stats for specific channel</li>
                </ul>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Statistics Types</h3>
                
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Server Statistics</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Overall server metrics including:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Total messages indexed</li>
                    <li>Active users count</li>
                    <li>Most active channels</li>
                    <li>Peak activity times</li>
                    <li>Trending topics</li>
                    <li>Cache performance metrics</li>
                  </ul>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mt-3">
                    /stats scope: Server Statistics
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">User Activity</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Individual user engagement metrics:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Message count and frequency</li>
                    <li>Most active channels</li>
                    <li>Favorite topics</li>
                    <li>Activity patterns (time of day)</li>
                    <li>Engagement score</li>
                  </ul>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mt-3">
                    /stats scope: User Activity user: @alice
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Channel Analytics</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Channel-specific insights:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Message volume over time</li>
                    <li>Top contributors</li>
                    <li>Response times</li>
                    <li>Topic distribution</li>
                    <li>Activity trends</li>
                  </ul>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs mt-3">
                    /stats scope: Channel Analytics channel: #general
                  </code>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/wrapped</h2>
              <p className="text-gray-300 mb-4">
                Generate a Spotify Wrapped-style yearly summary of server activity. Perfect for end-of-year celebrations or milestone reviews.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /wrapped year: &lt;YYYY&gt; [user: @user]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">year</strong> (required): Year to generate summary for (e.g., 2025)</li>
                  <li><strong className="text-white">user</strong> (optional): Generate personal wrapped for specific user</li>
                </ul>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Wrapped Includes</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-semibold text-[#5865F2] mb-2">Server Wrapped</h4>
                    <ul className="list-disc list-inside text-gray-300 text-xs space-y-1">
                      <li>Top contributors</li>
                      <li>Most active month</li>
                      <li>Popular channels</li>
                      <li>Trending topics</li>
                      <li>Milestone moments</li>
                      <li>Growth statistics</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-[#5865F2] mb-2">Personal Wrapped</h4>
                    <ul className="list-disc list-inside text-gray-300 text-xs space-y-1">
                      <li>Message count</li>
                      <li>Favorite channels</li>
                      <li>Most discussed topics</li>
                      <li>Peak activity times</li>
                      <li>Engagement score</li>
                      <li>Year highlights</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Examples</h3>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Server-wide wrapped:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /wrapped year: 2025
                  </code>
                </div>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Personal wrapped:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /wrapped year: 2025 user: @john
                  </code>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Use Cases</h2>
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Community Management</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Track server health and identify engagement patterns:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Monitor which channels need more activity</li>
                    <li>Identify power users for moderation roles</li>
                    <li>Track growth trends over time</li>
                    <li>Understand peak activity times for events</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Team Insights</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Understand team collaboration patterns:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>See who&apos;s most active in project channels</li>
                    <li>Identify knowledge silos</li>
                    <li>Track response times</li>
                    <li>Measure team engagement</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Content Planning</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Use analytics to inform content strategy:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Identify trending topics for discussion</li>
                    <li>Find best times to post announcements</li>
                    <li>Understand what content resonates</li>
                    <li>Track engagement with specific topics</li>
                  </ul>
                </div>
              </div>
            </section>

            <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg mb-6">
              <h4 className="text-sm font-semibold mb-2">📊 Privacy Note</h4>
              <p className="text-gray-300 text-sm">
                All analytics are aggregated and anonymized where appropriate. User-specific stats are only visible to the user themselves and server administrators.
              </p>
            </div>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/commands/search" className="text-[#5865F2] hover:underline">
                ← Search Commands
              </Link>
              <Link href="/docs/commands/utility" className="text-[#5865F2] hover:underline">
                Utility Commands →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
