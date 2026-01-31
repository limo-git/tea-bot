import Link from 'next/link';

export default function Installation() {
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
                <li><Link href="/docs/installation" className="text-[#5865F2] hover:text-white transition-colors">Installation</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Installation</h1>
            <p className="text-xl text-gray-400">
              Add TeaL;DR to your Discord server in under 60 seconds.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Prerequisites</h2>
              <p className="text-gray-300 mb-4">
                Before installing TeaL;DR, ensure you have:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 mb-6">
                <li>Administrator permissions or &quot;Manage Server&quot; permission in your Discord server</li>
                <li>A Discord server with at least one text channel</li>
                <li>Understanding of your server&apos;s privacy requirements</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Step 1: Invite the Bot</h2>
              <p className="text-gray-300 mb-4">
                Click the button below to open the Discord OAuth2 authorization page:
              </p>
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-4">
                <a
                  href="https://discord.com/api/oauth2/authorize?client_id=1466768259369013333&permissions=274877959168&scope=bot%20applications.commands"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-8 py-4 bg-[#5865F2] rounded-xl font-bold text-lg transition-all duration-300 hover:shadow-xl hover:shadow-[#5865F2]/50 hover:scale-105"
                >
                  Add TeaL;DR to Discord
                </a>
              </div>
              <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg">
                <p className="text-sm text-gray-300">
                  <strong>Note:</strong> You will be redirected to Discord&apos;s authorization page where you can select which server to add the bot to.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Step 2: Select Your Server</h2>
              <p className="text-gray-300 mb-4">
                On the Discord authorization page:
              </p>
              <ol className="list-decimal list-inside text-gray-300 space-y-3 mb-6">
                <li>Select the server you want to add TeaL;DR to from the dropdown menu</li>
                <li>Review the requested permissions (see below for details)</li>
                <li>Click &quot;Authorize&quot; to complete the installation</li>
                <li>Complete the CAPTCHA verification if prompted</li>
              </ol>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Step 3: Verify Installation</h2>
              <p className="text-gray-300 mb-4">
                After authorization, TeaL;DR will appear in your server&apos;s member list. To verify it&apos;s working:
              </p>
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-4">
                <p className="text-sm text-gray-400 mb-2">Run this command in any channel:</p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono">
                  /help
                </code>
              </div>
              <p className="text-gray-300 mb-4">
                If the bot responds with a list of available commands, the installation was successful.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Required Permissions</h2>
              <p className="text-gray-300 mb-4">
                TeaL;DR requires the following permissions to function properly:
              </p>
              <div className="space-y-3">
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Read Messages/View Channels</h3>
                  <p className="text-gray-300 text-sm">
                    Required to index messages and respond to commands. The bot will only index channels it has access to.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Send Messages</h3>
                  <p className="text-gray-300 text-sm">
                    Required to send search results, summaries, and command responses.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Embed Links</h3>
                  <p className="text-gray-300 text-sm">
                    Required to display formatted responses with rich embeds for better readability.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Read Message History</h3>
                  <p className="text-gray-300 text-sm">
                    Required to index historical messages and provide search functionality for past conversations.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Use Slash Commands</h3>
                  <p className="text-gray-300 text-sm">
                    Required to register and respond to slash commands like /ask, /recap, and /stats.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Add Reactions</h3>
                  <p className="text-gray-300 text-sm">
                    Required for interactive features like quizzes and feedback collection.
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Initial Configuration</h2>
              <p className="text-gray-300 mb-4">
                After installation, the bot will automatically start indexing new messages. To configure initial settings:
              </p>
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-4">
                <h3 className="text-lg font-semibold mb-3">Exclude Private Channels</h3>
                <p className="text-gray-300 text-sm mb-3">
                  If you have private channels that should not be indexed:
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: Exclude Channel channel: #private-channel
                </code>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-4">
                <h3 className="text-lg font-semibold mb-3">Set Message Retention</h3>
                <p className="text-gray-300 text-sm mb-3">
                  Configure how long messages are stored (default: 30 days):
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: Set Retention Period days: 60
                </code>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                <h3 className="text-lg font-semibold mb-3">Customize Bot Personality</h3>
                <p className="text-gray-300 text-sm mb-3">
                  Adjust the bot&apos;s response style:
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /customize persona: Professional
                </code>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Troubleshooting</h2>
              <div className="space-y-4">
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Bot doesn&apos;t respond to commands</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>Verify the bot has &quot;Use Slash Commands&quot; permission</li>
                    <li>Check if the bot is online (green status indicator)</li>
                    <li>Try using commands in a different channel</li>
                    <li>Wait a few minutes for slash commands to register</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Search returns no results</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                    <li>The bot needs time to index existing messages (up to 24 hours for large servers)</li>
                    <li>Verify the bot has &quot;Read Message History&quot; permission</li>
                    <li>Check if the channel is excluded from indexing</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Bot was removed accidentally</h3>
                  <p className="text-gray-300 text-sm">
                    Simply re-invite the bot using the authorization link. Your previous configuration will be restored 
                    if you re-add within 30 days.
                  </p>
                </div>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs" className="text-[#5865F2] hover:underline">
                ← Back to Introduction
              </Link>
              <Link href="/docs/quickstart" className="text-[#5865F2] hover:underline">
                Quick Start Guide →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
