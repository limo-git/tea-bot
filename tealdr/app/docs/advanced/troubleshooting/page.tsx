import Link from 'next/link';

export default function Troubleshooting() {
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
            <Link href="/" className="text-gray-400 hover:text-white transition-colors duration-300">Home</Link>
            <Link href="/docs" className="text-[#5865F2]">Docs</Link>
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
                <li><Link href="/docs/advanced/troubleshooting" className="text-[#5865F2] hover:text-white transition-colors">Troubleshooting</Link></li>
              </ul>
            </div>
          </nav>
        </aside>

        <main className="flex-1 lg:ml-64 px-6 py-12 max-w-4xl">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">Troubleshooting</h1>
            <p className="text-xl text-gray-400">
              Common issues and their solutions.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Bot Not Responding</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Slash Commands Not Appearing</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Commands don&apos;t show up when typing /</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Wait 5-10 minutes after adding the bot for commands to register</li>
                    <li>Verify bot has &quot;Use Application Commands&quot; permission</li>
                    <li>Try typing the full command: <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/help</code></li>
                    <li>Kick and re-invite the bot with proper permissions</li>
                    <li>Check if bot is online (green status indicator)</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Bot Shows Offline</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Bot appears offline or shows gray status</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Check status page for known outages</li>
                    <li>Wait 2-3 minutes for bot to reconnect</li>
                    <li>Contact support if offline for more than 10 minutes</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Commands Return Errors</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> &quot;Application did not respond&quot; or timeout errors</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Verify bot has required permissions in the channel</li>
                    <li>Check if you&apos;re hitting rate limits (wait 30 seconds)</li>
                    <li>Try the command in a different channel</li>
                    <li>Simplify your query if it&apos;s very long or complex</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Search Issues</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">No Search Results</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> /ask returns &quot;No relevant messages found&quot;</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Wait 24 hours after installation for full indexing</li>
                    <li>Check if the channel is excluded: <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/settings action: View Excluded Channels</code></li>
                    <li>Verify bot has &quot;Read Message History&quot; permission</li>
                    <li>Try broader search terms</li>
                    <li>Check retention period hasn&apos;t expired old messages</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Irrelevant Results</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Search returns unrelated messages</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Use more specific, descriptive queries</li>
                    <li>Add channel or user filters to narrow results</li>
                    <li>Use natural language instead of keywords</li>
                    <li>Clear context with <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/clear</code> and try again</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Slow Search Performance</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Searches take more than 10 seconds</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Use channel filters to reduce search scope</li>
                    <li>Reduce retention period for faster indexing</li>
                    <li>Exclude high-traffic channels from indexing</li>
                    <li>Check cache statistics: <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/stats scope: Server Statistics</code></li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Permission Problems</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Cannot Use Admin Commands</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> &quot;You don&apos;t have permission to use this command&quot;</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Verify you have Administrator or Manage Server permission</li>
                    <li>Check your role hierarchy in server settings</li>
                    <li>Ask server owner to grant you appropriate permissions</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Bot Cannot Read Messages</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Bot doesn&apos;t index certain channels</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Check channel permissions for bot role</li>
                    <li>Ensure bot has &quot;View Channel&quot; permission</li>
                    <li>Verify channel isn&apos;t manually excluded</li>
                    <li>Check if channel is in a category with permission overrides</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Data and Storage</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Messages Not Being Indexed</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Recent messages don&apos;t appear in searches</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Wait 1-2 minutes for real-time indexing</li>
                    <li>Check bot is online and has permissions</li>
                    <li>Verify channel isn&apos;t excluded from indexing</li>
                    <li>Check if you&apos;ve reached storage limits</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Old Messages Disappeared</h3>
                  <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> Previously searchable messages no longer found</p>
                  <p className="text-gray-300 text-sm mb-3"><strong>Solutions:</strong></p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Check retention period: <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/settings action: View Retention Period</code></li>
                    <li>Messages older than retention period are automatically deleted</li>
                    <li>Increase retention if you need longer history</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Rate Limits and Quotas</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Rate Limit Exceeded</h3>
                <p className="text-gray-300 text-sm mb-3"><strong>Symptoms:</strong> &quot;You&apos;re doing that too fast&quot; error</p>
                <p className="text-gray-300 text-sm mb-3"><strong>Current Limits:</strong></p>
                <ul className="list-disc list-inside text-gray-300 text-sm space-y-2 mb-3">
                  <li>Search commands: 10 per minute per user</li>
                  <li>Export commands: 3 per hour per user</li>
                  <li>Admin commands: 20 per minute per server</li>
                </ul>
                <p className="text-gray-300 text-sm"><strong>Solution:</strong> Wait for the cooldown period and try again.</p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Getting Help</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Before Contacting Support</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Check this troubleshooting guide</li>
                    <li>Verify bot permissions in server settings</li>
                    <li>Try the command in a different channel</li>
                    <li>Check if issue persists after 10 minutes</li>
                    <li>Note exact error messages</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Contact Support</h3>
                  <p className="text-gray-300 text-sm mb-3">If issues persist, reach out through:</p>
                  <ul className="space-y-2 text-gray-300 text-sm">
                    <li>📧 Email: <a href="mailto:support@tealdr.com" className="text-[#5865F2] hover:underline">support@tealdr.com</a></li>
                    <li>🐙 GitHub Issues: <a href="https://github.com/limo-git/tea-bot/issues" target="_blank" rel="noopener noreferrer" className="text-[#5865F2] hover:underline">github.com/limo-git/tea-bot</a></li>
                    <li>💬 Discord Server: Join our support server for live help</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-xl">
                  <h3 className="text-lg font-semibold mb-3">Include in Support Requests</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Server ID and channel ID</li>
                    <li>Exact command you tried</li>
                    <li>Error message (screenshot if possible)</li>
                    <li>When the issue started</li>
                    <li>Steps you&apos;ve already tried</li>
                  </ul>
                </div>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/advanced/architecture" className="text-[#5865F2] hover:underline">
                ← Architecture
              </Link>
              <Link href="/docs" className="text-[#5865F2] hover:underline">
                Back to Docs Home →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
