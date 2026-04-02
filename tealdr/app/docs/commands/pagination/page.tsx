import Link from 'next/link';

export default function PaginationDocs() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a] border-b border-[#5865F2]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight">TeaL;DR</span>
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
                <li><Link href="/docs/commands/pagination" className="text-[#5865F2] hover:text-white transition-colors">Pagination & UI</Link></li>
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
            <div className="inline-block px-3 py-1 bg-[#5865F2] text-white text-xs font-bold mb-4">
              NEW FEATURE
            </div>
            <h1 className="text-4xl font-bold mb-4">Pagination & Interactive UI</h1>
            <p className="text-xl text-gray-400">
              Navigate through long responses with intuitive button controls and source viewing.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">Overview</h2>
              <p className="text-gray-300 mb-4">
                Both <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/ask</code> and <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/lookup</code> commands now feature 
                interactive pagination controls, replacing the old emoji reaction system with modern button-based navigation.
              </p>

              <div className="p-6 bg-[#111111] border-2 border-[#5865F2]/30 rounded-lg mb-6">
                <h3 className="text-xl font-bold mb-3 text-[#5865F2]">Key Features</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span><strong>Arrow Navigation:</strong> Use ◀️ and ▶️ buttons to navigate between pages</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span><strong>Source Toggle:</strong> Switch between answer and detailed source information</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span><strong>Feedback Buttons:</strong> Give thumbs up 👍 or down 👎 to help improve results</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span><strong>Smart Splitting:</strong> Long responses automatically split at paragraph boundaries</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span><strong>User-Specific:</strong> Only you can interact with your query results</span>
                  </li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">/ask Command Pagination</h2>
              <p className="text-gray-300 mb-4">
                When you use <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/ask</code>, long AI-generated responses are automatically paginated.
              </p>

              <div className="bg-[#0a0a0a] border border-[#5865F2]/30 p-4 rounded-lg mb-4 font-mono text-sm">
                <div className="text-[#5865F2] mb-2">Example:</div>
                <div className="text-gray-400">
                  /ask query: what did we discuss about Docker?
                </div>
              </div>

              <div className="p-6 bg-[#111111] border-2 border-[#5865F2]/30 rounded-lg mb-6">
                <h3 className="text-lg font-bold mb-3">Button Layout</h3>
                <div className="bg-[#0a0a0a] p-4 rounded border border-[#5865F2]/20 font-mono text-sm mb-4">
                  [◀️] [▶️] [📊 Show Sources] [👍] [👎]
                  <br />
                  <span className="text-gray-500">Page 1/3 • 10 sources used</span>
                </div>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong>◀️ Previous:</strong> Go to previous page (disabled on first page)</li>
                  <li><strong>▶️ Next:</strong> Go to next page (disabled on last page)</li>
                  <li><strong>📊 Show Sources:</strong> Toggle between answer and source details</li>
                  <li><strong>👍 Thumbs Up:</strong> Mark answer as helpful</li>
                  <li><strong>👎 Thumbs Down:</strong> Mark answer as not helpful</li>
                </ul>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border-l-4 border-[#5865F2] mb-4">
                <p className="text-sm text-gray-300">
                  <strong className="text-[#5865F2]">💡 Tip:</strong> Responses are split at ~1800 characters per page, 
                  breaking at paragraph boundaries for better readability.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">/lookup Command Pagination</h2>
              <p className="text-gray-300 mb-4">
                The <code className="text-[#5865F2] bg-[#5865F2]/10 px-2 py-1">/lookup</code> command shows exact messages with pagination controls.
              </p>

              <div className="bg-[#0a0a0a] border border-[#5865F2]/30 p-4 rounded-lg mb-4 font-mono text-sm">
                <div className="text-[#5865F2] mb-2">Example:</div>
                <div className="text-gray-400">
                  /lookup clues: docker deployment
                </div>
              </div>

              <div className="p-6 bg-[#111111] border-2 border-[#5865F2]/30 rounded-lg mb-6">
                <h3 className="text-lg font-bold mb-3">Results View</h3>
                <p className="text-gray-300 mb-3">Shows 10 messages per page with:</p>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Author name</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Timestamp (auto-converted to your timezone)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Channel name</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Message content (truncated if long)</span>
                  </li>
                </ul>
              </div>

              <div className="p-6 bg-[#111111] border-2 border-[#5865F2]/30 rounded-lg mb-6">
                <h3 className="text-lg font-bold mb-3">Sources View</h3>
                <p className="text-gray-300 mb-3">Click "📊 Show Sources" to see detailed metadata:</p>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Author ID</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Message ID</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Channel ID</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#5865F2]">•</span>
                    <span>Relevance score (percentage)</span>
                  </li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">Behavior & Limits</h2>
              
              <div className="space-y-4">
                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg">
                  <h3 className="font-bold mb-2">Page Limits</h3>
                  <ul className="space-y-1 text-gray-300 text-sm">
                    <li><strong>/ask:</strong> ~1800 characters per page</li>
                    <li><strong>/lookup:</strong> 10 messages per page</li>
                    <li><strong>Sources:</strong> 10 sources per page</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg">
                  <h3 className="font-bold mb-2">Timeout</h3>
                  <p className="text-gray-300 text-sm">
                    Buttons remain active for 5 minutes (300 seconds). After timeout, buttons are disabled but the message remains visible.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg">
                  <h3 className="font-bold mb-2">Feedback</h3>
                  <p className="text-gray-300 text-sm">
                    You can only give feedback (👍/👎) once per query. After voting, feedback buttons are disabled and your choice is highlighted.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg">
                  <h3 className="font-bold mb-2">Privacy</h3>
                  <p className="text-gray-300 text-sm">
                    Only the user who ran the command can interact with the pagination buttons. Others will see a message if they try to click.
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">Migration from Reactions</h2>
              <p className="text-gray-300 mb-4">
                The old emoji reaction system has been completely replaced with buttons:
              </p>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-[#111111] border border-red-500/30 rounded-lg">
                  <h3 className="font-bold mb-2 text-red-400">❌ Old System</h3>
                  <ul className="space-y-1 text-gray-400 text-sm">
                    <li>👍 reaction for feedback</li>
                    <li>👎 reaction for feedback</li>
                    <li>📊 reaction for sources</li>
                    <li>Separate messages for sources</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg">
                  <h3 className="font-bold mb-2 text-[#5865F2]">✅ New System</h3>
                  <ul className="space-y-1 text-gray-300 text-sm">
                    <li>👍 button for feedback</li>
                    <li>👎 button for feedback</li>
                    <li>📊 button toggles sources in same message</li>
                    <li>◀️ ▶️ buttons for navigation</li>
                  </ul>
                </div>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border-l-4 border-[#5865F2]">
                <p className="text-sm text-gray-300">
                  <strong className="text-[#5865F2]">💡 Why the change?</strong> Buttons provide a cleaner, more intuitive interface 
                  and allow for better control over who can interact with results.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4 text-[#5865F2]">Related Commands</h2>
              <div className="grid gap-4">
                <Link href="/docs/commands/search" className="block p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg hover:border-[#5865F2] transition-colors">
                  <h3 className="font-bold mb-1">Search Commands</h3>
                  <p className="text-sm text-gray-400">Learn about /ask and /lookup in detail</p>
                </Link>
                <Link href="/docs/commands/admin" className="block p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg hover:border-[#5865F2] transition-colors">
                  <h3 className="font-bold mb-1">Admin Commands</h3>
                  <p className="text-sm text-gray-400">Manage bot settings and private sessions</p>
                </Link>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
