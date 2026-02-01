import Link from 'next/link';

export default function AdminCommands() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a] border-b border-[#5865F2]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight">teal;dr</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/" className="text-[#a0a0a0] hover:text-[#5865F2] transition-colors duration-200">HOME</Link>
            <Link href="/docs" className="text-[#5865F2] font-bold">DOCS</Link>
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
                <li><Link href="/docs/commands/admin" className="text-[#5865F2] hover:text-white transition-colors">Admin</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Admin Commands</h1>
            <p className="text-xl text-gray-400">
              Configuration and management commands for server administrators.
            </p>
          </div>

          <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg mb-8">
            <p className="text-sm text-gray-300">
              <strong>⚠️ Administrator Only:</strong> All commands on this page require Discord administrator permissions or the &quot;Manage Server&quot; permission.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/settings</h2>
              <p className="text-gray-300 mb-4">
                Configure bot behavior, manage channels, and control data retention. This is the primary admin command for bot configuration.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: &lt;action_type&gt; [channel: #channel] [days: number] [confirm: yes]
                </code>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-lg font-semibold">Available Actions</h3>
                
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Exclude Channel</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Prevent the bot from indexing messages in a specific channel.
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: Exclude Channel channel: #private-chat
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Include Channel</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Re-enable indexing for a previously excluded channel.
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: Include Channel channel: #general
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">Set Retention Period</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Configure how long messages are stored (7-90 days).
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: Set Retention Period days: 60
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-3">View All Settings</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Display current configuration for your server.
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: View All Settings
                  </code>
                </div>

                <div className="p-6 bg-[#111111] border border-red-500/30 rounded-xl">
                  <h4 className="text-md font-semibold text-red-400 mb-3">Clear All Data</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Permanently delete all indexed data for your server. Requires confirmation.
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-xs">
                    /settings action: Clear All Data confirm: yes
                  </code>
                  <p className="text-red-400 text-xs mt-2">⚠️ This action is irreversible</p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">/customize</h2>
              <p className="text-gray-300 mb-4">
                Customize the bot&apos;s personality and response style to match your server&apos;s culture.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold mb-3">Syntax</h3>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /customize persona: &lt;Professional|Friendly|Technical|Concise&gt;
                </code>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">Professional</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Formal, business-focused tone. Best for work servers and professional communities.
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Formal language</li>
                    <li>• Concise responses</li>
                    <li>• Business terminology</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">Friendly</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Casual, conversational tone. Best for gaming and community servers.
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Casual language</li>
                    <li>• Warm responses</li>
                    <li>• Community-focused</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">Technical</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Detailed, precise responses. Best for developer and technical communities.
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Technical terminology</li>
                    <li>• Detailed explanations</li>
                    <li>• Code-focused</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">Concise</h4>
                  <p className="text-gray-300 text-sm mb-3">
                    Brief, to-the-point responses. Best for high-traffic servers.
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Short responses</li>
                    <li>• Key points only</li>
                    <li>• Minimal elaboration</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Admin Best Practices</h2>
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Privacy First</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Exclude channels containing sensitive information (HR, moderation logs)</li>
                    <li>Review excluded channels list regularly</li>
                    <li>Inform members about bot indexing in server rules</li>
                    <li>Set appropriate retention periods for your use case</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Performance Optimization</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Exclude high-traffic bot channels to reduce noise</li>
                    <li>Use shorter retention periods for very active servers</li>
                    <li>Monitor cache statistics with /stats</li>
                    <li>Clear old data periodically if storage is a concern</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">User Experience</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Choose a persona that matches your server culture</li>
                    <li>Announce bot features to your community</li>
                    <li>Create a #bot-commands channel for testing</li>
                    <li>Document your server&apos;s bot usage guidelines</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Permission Requirements</h2>
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                <p className="text-gray-300 mb-4">
                  To use admin commands, users must have one of the following:
                </p>
                <ul className="list-disc list-inside text-gray-300 space-y-2">
                  <li><strong className="text-white">Administrator</strong> permission in Discord</li>
                  <li><strong className="text-white">Manage Server</strong> permission</li>
                  <li>Server <strong className="text-white">Owner</strong> role</li>
                </ul>
                <p className="text-gray-400 text-sm mt-4">
                  The bot will verify permissions before executing any admin command and will return an error if the user lacks sufficient permissions.
                </p>
              </div>
            </section>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/commands/utility" className="text-[#5865F2] hover:underline">
                ← Utility Commands
              </Link>
              <Link href="/docs/config/settings" className="text-[#5865F2] hover:underline">
                Bot Settings →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
