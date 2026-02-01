import Link from 'next/link';

export default function BotSettings() {
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
                <li><Link href="/docs/commands/analytics" className="text-gray-400 hover:text-white transition-colors">Analytics</Link></li>
                <li><Link href="/docs/commands/utility" className="text-gray-400 hover:text-white transition-colors">Utility</Link></li>
                <li><Link href="/docs/commands/admin" className="text-gray-400 hover:text-white transition-colors">Admin</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Configuration</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/config/settings" className="text-[#5865F2] hover:text-white transition-colors">Bot Settings</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Bot Settings</h1>
            <p className="text-xl text-gray-400">
              Configure TeaL;DR to match your server&apos;s needs.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Overview</h2>
              <p className="text-gray-300 mb-4">
                TeaL;DR provides extensive configuration options through the <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/settings</code> command. 
                All settings require administrator permissions to modify.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Channel Management</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Exclude Channel from Indexing</h3>
                <p className="text-gray-300 mb-4">
                  Prevent the bot from indexing messages in specific channels. Useful for private channels, admin channels, or bot-only channels.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /settings action: Exclude Channel channel: #private-channel
                </code>
                <div className="p-3 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded text-sm text-gray-300">
                  <strong>Note:</strong> Existing messages in the channel will remain indexed. Use &quot;Clear Channel Data&quot; to remove them.
                </div>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Include Previously Excluded Channel</h3>
                <p className="text-gray-300 mb-4">
                  Re-enable indexing for a previously excluded channel.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: Include Channel channel: #general
                </code>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">View Excluded Channels</h3>
                <p className="text-gray-300 mb-4">
                  List all channels currently excluded from indexing.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: View Excluded Channels
                </code>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Data Retention</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Set Retention Period</h3>
                <p className="text-gray-300 mb-4">
                  Configure how long messages are stored before automatic deletion. Default is 30 days.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /settings action: Set Retention Period days: 60
                </code>
                <div className="space-y-2 text-sm text-gray-300">
                  <p><strong>Allowed values:</strong> 7-90 days</p>
                  <p><strong>Recommended:</strong> 30 days for most servers, 60-90 days for archival purposes</p>
                </div>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">View Current Retention</h3>
                <p className="text-gray-300 mb-4">
                  Check the current retention period setting.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: View Retention Period
                </code>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Bot Personality</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Customize Response Style</h3>
                <p className="text-gray-300 mb-4">
                  Adjust how the bot responds to queries. Available personas:
                </p>
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div className="p-4 bg-[#0a0a0a] border border-[#1a1a1a] rounded">
                    <h4 className="font-semibold text-white mb-2">Professional</h4>
                    <p className="text-sm text-gray-400">Formal, concise, business-focused responses</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] border border-[#1a1a1a] rounded">
                    <h4 className="font-semibold text-white mb-2">Friendly</h4>
                    <p className="text-sm text-gray-400">Casual, conversational tone with personality</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] border border-[#1a1a1a] rounded">
                    <h4 className="font-semibold text-white mb-2">Technical</h4>
                    <p className="text-sm text-gray-400">Detailed, precise, developer-oriented</p>
                  </div>
                  <div className="p-4 bg-[#0a0a0a] border border-[#1a1a1a] rounded">
                    <h4 className="font-semibold text-white mb-2">Concise</h4>
                    <p className="text-sm text-gray-400">Brief, to-the-point responses</p>
                  </div>
                </div>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /customize persona: Professional
                </code>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Data Management</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Clear Channel Data</h3>
                <p className="text-gray-300 mb-4">
                  Permanently delete all indexed messages from a specific channel.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-3">
                  /settings action: Clear Channel Data channel: #old-channel
                </code>
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-gray-300">
                  <strong>⚠️ Warning:</strong> This action is irreversible. All search history for this channel will be permanently deleted.
                </div>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Clear All Server Data</h3>
                <p className="text-gray-300 mb-4">
                  Delete all indexed data for your entire server. This is useful before removing the bot or for privacy compliance.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-3">
                  /settings action: Clear All Data confirm: yes
                </code>
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-gray-300">
                  <strong>⚠️ Warning:</strong> This will delete all messages, embeddings, and configuration. Requires confirmation.
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">View Current Configuration</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Display All Settings</h3>
                <p className="text-gray-300 mb-4">
                  View a comprehensive overview of all current bot settings for your server.
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /settings action: View All Settings
                </code>
                <p className="text-sm text-gray-400">
                  This displays: excluded channels, retention period, bot persona, indexing status, and storage usage.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Best Practices</h2>
              <div className="space-y-4">
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Privacy-Sensitive Channels</h3>
                  <p className="text-gray-300 text-sm">
                    Always exclude channels containing sensitive information (HR, moderation logs, private discussions) from indexing.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Retention Period</h3>
                  <p className="text-gray-300 text-sm">
                    Balance between searchability and storage. 30 days works for most active servers. Increase for archival needs.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Regular Audits</h3>
                  <p className="text-gray-300 text-sm">
                    Periodically review excluded channels and retention settings to ensure they match your current needs.
                  </p>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-2">Bot Personality</h3>
                  <p className="text-gray-300 text-sm">
                    Choose a persona that matches your server culture. Professional for work servers, Friendly for community servers.
                  </p>
                </div>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/commands/admin" className="text-[#5865F2] hover:underline">
                ← Admin Commands
              </Link>
              <Link href="/docs/config/permissions" className="text-[#5865F2] hover:underline">
                Permissions →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
