import Link from 'next/link';

export default function DocsHome() {
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
                <li><Link href="/docs" className="text-[#5865F2] hover:text-white transition-colors">Introduction</Link></li>
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
                <li><Link href="/docs/advanced/troubleshooting" className="text-gray-400 hover:text-white transition-colors">Troubleshooting</Link></li>
              </ul>
            </div>
          </nav>
        </aside>

        <main className="flex-1 lg:ml-64 px-6 py-12 max-w-4xl">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">Documentation</h1>
            <p className="text-xl text-gray-400">
              Complete guide to using TeaL;DR, the AI-powered Discord search bot.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Introduction</h2>
              <p className="text-gray-300 mb-4">
                TeaL;DR is a Discord bot that provides semantic search capabilities for your server&apos;s message history. 
                Using advanced AI embeddings and natural language processing, TeaL;DR enables you to search through 
                conversations using plain English queries, generate summaries, and gain insights from your server&apos;s data.
              </p>
              <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-lg mb-4">
                <p className="text-sm text-gray-400 mb-2">Key Features:</p>
                <ul className="list-disc list-inside text-gray-300 space-y-1">
                  <li>Semantic search using AI embeddings</li>
                  <li>Conversation summaries and recaps</li>
                  <li>Server analytics and statistics</li>
                  <li>Data export in multiple formats</li>
                  <li>Interactive features (quizzes, wrapped summaries)</li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">How It Works</h2>
              <div className="space-y-4 text-gray-300">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-3">1. Message Indexing</h3>
                  <p>
                    TeaL;DR automatically indexes messages as they are sent in your server. Each message is processed 
                    through Google Gemini AI to generate semantic embeddings, which capture the meaning and context of the text.
                  </p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-3">2. Semantic Search</h3>
                  <p>
                    When you search using <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/ask</code>, 
                    your query is converted into an embedding and compared against stored message embeddings using cosine 
                    similarity. This allows the bot to find relevant messages even if they don&apos;t contain exact keyword matches.
                  </p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-3">3. AI-Powered Responses</h3>
                  <p>
                    Retrieved messages are processed through an AI model to generate coherent summaries, answer questions, 
                    and provide context-aware responses. The bot maintains conversation history for follow-up questions.
                  </p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-3">4. Data Privacy</h3>
                  <p>
                    All server data is isolated and never shared between servers. Messages are automatically deleted after 
                    30 days (configurable), and you can exclude specific channels from indexing at any time.
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Quick Links</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <Link href="/docs/installation" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Installation →</h3>
                  <p className="text-gray-400">Add TeaL;DR to your Discord server in under 60 seconds.</p>
                </Link>

                <Link href="/docs/commands/search" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Search Commands →</h3>
                  <p className="text-gray-400">Learn how to search through your server history effectively.</p>
                </Link>

                <Link href="/docs/config/settings" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Configuration →</h3>
                  <p className="text-gray-400">Customize bot behavior and manage permissions.</p>
                </Link>

                <Link href="/docs/advanced/troubleshooting" className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl hover:border-[#5865F2] transition-all group">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[#5865F2] transition-colors">Troubleshooting →</h3>
                  <p className="text-gray-400">Common issues and their solutions.</p>
                </Link>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">System Requirements</h2>
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">✓</span>
                    <div>
                      <strong>Discord Server:</strong> You must have administrator permissions or the &quot;Manage Server&quot; permission
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">✓</span>
                    <div>
                      <strong>Bot Permissions:</strong> Read Messages, Send Messages, Embed Links, Read Message History
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">✓</span>
                    <div>
                      <strong>Storage:</strong> Approximately 1MB per 1000 messages indexed
                    </div>
                  </li>
                </ul>
              </div>
            </section>

            <div className="p-6 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-xl">
              <h3 className="text-lg font-semibold mb-2">Need Help?</h3>
              <p className="text-gray-300 mb-4">
                If you encounter any issues or have questions, check the troubleshooting guide or contact support.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/limo-git/tea-bot" target="_blank" rel="noopener noreferrer" className="text-[#5865F2] hover:underline">
                  GitHub →
                </a>
                <a href="mailto:support@tealdr.com" className="text-[#5865F2] hover:underline">
                  Email Support →
                </a>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
