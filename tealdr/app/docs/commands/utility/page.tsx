import Link from 'next/link';

export default function UtilityCommands() {
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
                <li><Link href="/docs/commands/utility" className="text-[#5865F2] hover:text-white transition-colors">Utility</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Utility Commands</h1>
            <p className="text-xl text-gray-400">Export data, manage context, and access help resources.</p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/export</h2>
              <p className="text-gray-300 mb-4">
                Export search results or conversation data to various formats for external analysis, archival, or reporting.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /export query: &lt;search query&gt; format: &lt;CSV|JSON|Markdown|TXT&gt; [limit: number]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">query</strong> (required): Search query to export results for</li>
                  <li><strong className="text-white">format</strong> (required): Export format (CSV, JSON, Markdown, TXT)</li>
                  <li><strong className="text-white">limit</strong> (optional): Maximum number of results (default: 100, max: 1000)</li>
                </ul>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Export Formats</h3>
                
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">CSV (Comma-Separated Values)</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Best for: Spreadsheet analysis, data processing, statistical analysis
                  </p>
                  <p className="text-gray-400 text-xs mb-2">Includes columns:</p>
                  <code className="block text-xs text-gray-400 bg-[#0a0a0a] px-3 py-2 rounded">
                    timestamp, author, channel, content, relevance_score, message_id
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">JSON (JavaScript Object Notation)</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Best for: API integration, programmatic processing, structured data analysis
                  </p>
                  <p className="text-gray-400 text-xs mb-2">Includes full message metadata and nested structures</p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Markdown</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Best for: Documentation, reports, human-readable archives
                  </p>
                  <p className="text-gray-400 text-xs">Formatted with headers, links, and proper structure</p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">TXT (Plain Text)</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Best for: Simple archival, text processing, maximum compatibility
                  </p>
                  <p className="text-gray-400 text-xs">Clean text format with minimal formatting</p>
                </div>
              </div>

              <div className="space-y-3 mb-6">
                <h3 className="text-lg font-semibold">Examples</h3>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Export to CSV for analysis:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /export query: feature requests format: CSV limit: 500
                  </code>
                </div>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Export to JSON for API:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /export query: bug reports format: JSON
                  </code>
                </div>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg">
                <p className="text-sm text-gray-300">
                  <strong>Note:</strong> Export links expire after 24 hours. Download files are limited to 10MB.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/quiz</h2>
              <p className="text-gray-300 mb-4">
                Create an interactive Kahoot-style trivia game based on your server&apos;s message history.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /quiz num_questions: &lt;number&gt; time_period: &lt;period&gt; [difficulty: easy|medium|hard]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">num_questions</strong> (required): Number of questions (1-20)</li>
                  <li><strong className="text-white">time_period</strong> (required): Time range to pull questions from</li>
                  <li><strong className="text-white">difficulty</strong> (optional): Question difficulty level</li>
                </ul>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">How It Works</h3>
                <ol className="list-decimal list-inside text-gray-300 text-sm space-y-2">
                  <li>Bot analyzes messages from specified time period</li>
                  <li>Generates multiple-choice questions about discussions</li>
                  <li>Players react with emoji to answer (🅰️ 🅱️ ©️ 🇩)</li>
                  <li>Points awarded for correct answers and speed</li>
                  <li>Leaderboard displayed at the end</li>
                </ol>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/clear</h2>
              <p className="text-gray-300 mb-4">
                Clear your conversation context with the bot. Useful when starting a new topic or if the bot seems confused.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /clear
                </code>
                <p className="text-gray-400 text-sm mt-3">
                  This command takes no parameters and immediately clears your conversation history with the bot.
                </p>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg">
                <h4 className="text-sm font-semibold mb-2">When to Use</h4>
                <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                  <li>Starting a completely new search topic</li>
                  <li>Bot responses seem off-topic or confused</li>
                  <li>Want to reset follow-up question context</li>
                  <li>Privacy: clearing your interaction history</li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/help</h2>
              <p className="text-gray-300 mb-4">
                Display comprehensive help information about bot commands and features.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /help [command: command_name]
                </code>
                
                <h4 className="text-md font-semibold text-gray-300 mb-2">Parameters</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li><strong className="text-white">command</strong> (optional): Get detailed help for specific command</li>
                </ul>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Examples</h3>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">General help:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /help
                  </code>
                </div>
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <p className="text-sm text-gray-400 mb-2">Command-specific help:</p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm">
                    /help command: ask
                  </code>
                </div>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/commands/analytics" className="text-[#5865F2] hover:underline">
                ← Analytics Commands
              </Link>
              <Link href="/docs/commands/admin" className="text-[#5865F2] hover:underline">
                Admin Commands →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
