import Link from 'next/link';

export default function Permissions() {
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
                <li><Link href="/docs/commands/admin" className="text-gray-400 hover:text-white transition-colors">Admin</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Configuration</h3>
              <ul className="space-y-2">
                <li><Link href="/docs/config/settings" className="text-gray-400 hover:text-white transition-colors">Bot Settings</Link></li>
                <li><Link href="/docs/config/permissions" className="text-[#5865F2] hover:text-white transition-colors">Permissions</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Permissions</h1>
            <p className="text-xl text-gray-400">
              Understanding and configuring Discord permissions for TeaL;DR.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Required Permissions</h2>
              <p className="text-gray-300 mb-6">
                TeaL;DR requires specific Discord permissions to function properly. These permissions are requested during bot installation and can be reviewed in your server settings.
              </p>

              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Read Messages / View Channels</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Allows the bot to see channels and read message content for indexing.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>Message indexing and search functionality</li>
                        <li>Responding to commands in channels</li>
                        <li>Generating conversation summaries</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Send Messages</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Enables the bot to send search results and command responses.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>Displaying search results</li>
                        <li>Sending command responses</li>
                        <li>Error messages and notifications</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Embed Links</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Allows the bot to send rich embeds with formatted content.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>Formatted search results with metadata</li>
                        <li>Statistics displays and analytics</li>
                        <li>Rich command responses</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Read Message History</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Allows the bot to access historical messages for indexing.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>Initial indexing of existing messages</li>
                        <li>Backfilling message history</li>
                        <li>Complete search functionality</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Use Slash Commands</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Enables slash command functionality for bot interaction.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>All bot commands (/ask, /recap, /stats, etc.)</li>
                        <li>Command autocomplete</li>
                        <li>Parameter suggestions</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-[#5865F2]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-[#5865F2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-[#5865F2] mb-2">Add Reactions</h3>
                      <p className="text-gray-300 text-sm mb-3">
                        <strong>Purpose:</strong> Allows the bot to add reaction emojis to messages.
                      </p>
                      <p className="text-gray-400 text-sm mb-2"><strong>Required for:</strong></p>
                      <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                        <li>Interactive quiz features</li>
                        <li>Feedback collection (👍/👎)</li>
                        <li>User engagement features</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Managing Permissions</h2>
              
              <div className="space-y-6">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-4">Server-Wide Permissions</h3>
                  <p className="text-gray-300 text-sm mb-4">
                    To modify bot permissions at the server level:
                  </p>
                  <ol className="list-decimal list-inside text-gray-300 text-sm space-y-2">
                    <li>Go to Server Settings → Integrations</li>
                    <li>Find TeaL;DR in the list</li>
                    <li>Click &quot;Manage&quot; to view and modify permissions</li>
                    <li>Toggle permissions on or off as needed</li>
                  </ol>
                  <div className="p-3 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded mt-4 text-sm text-gray-300">
                    <strong>Note:</strong> Removing required permissions will cause certain features to stop working.
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-4">Channel-Specific Permissions</h3>
                  <p className="text-gray-300 text-sm mb-4">
                    To control bot access to specific channels:
                  </p>
                  <ol className="list-decimal list-inside text-gray-300 text-sm space-y-2">
                    <li>Right-click the channel → Edit Channel</li>
                    <li>Go to Permissions tab</li>
                    <li>Add TeaL;DR bot role</li>
                    <li>Set permissions (allow/deny/inherit)</li>
                  </ol>
                  <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded mt-4 text-sm text-gray-300">
                    <strong>Tip:</strong> Use channel permissions to prevent indexing of private channels instead of manually excluding them.
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-xl font-semibold text-[#5865F2] mb-4">Role-Based Access</h3>
                  <p className="text-gray-300 text-sm mb-4">
                    The bot respects Discord&apos;s role hierarchy:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Bot can only index channels it has access to</li>
                    <li>Admin commands require user to have Administrator or Manage Server permission</li>
                    <li>Bot role position affects what it can access</li>
                    <li>Private channels require explicit bot access</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Permission Best Practices</h2>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">✓ Recommended</h3>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>• Grant all required permissions during installation</li>
                    <li>• Use channel permissions to control access</li>
                    <li>• Review bot permissions quarterly</li>
                    <li>• Document permission changes</li>
                    <li>• Test bot functionality after changes</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-orange-400 mb-3">✗ Avoid</h3>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>• Removing required permissions</li>
                    <li>• Granting Administrator permission</li>
                    <li>• Inconsistent channel permissions</li>
                    <li>• Allowing bot in sensitive channels</li>
                    <li>• Ignoring permission warnings</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Troubleshooting Permissions</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Bot Can&apos;t See Channels</h3>
                  <p className="text-gray-300 text-sm mb-2"><strong>Check:</strong></p>
                  <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                    <li>Bot has &quot;View Channels&quot; permission</li>
                    <li>Channel isn&apos;t private without bot access</li>
                    <li>Category permissions aren&apos;t blocking access</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Commands Not Working</h3>
                  <p className="text-gray-300 text-sm mb-2"><strong>Check:</strong></p>
                  <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                    <li>Bot has &quot;Use Application Commands&quot; permission</li>
                    <li>Bot has &quot;Send Messages&quot; in the channel</li>
                    <li>Commands have been registered (wait 5-10 minutes)</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Missing Search Results</h3>
                  <p className="text-gray-300 text-sm mb-2"><strong>Check:</strong></p>
                  <ul className="list-disc list-inside text-gray-400 text-sm space-y-1">
                    <li>Bot has &quot;Read Message History&quot; permission</li>
                    <li>Bot had access when messages were sent</li>
                    <li>Channel isn&apos;t excluded from indexing</li>
                  </ul>
                </div>
              </div>
            </section>

            <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg mb-6">
              <h4 className="text-sm font-semibold mb-2">🔒 Security Note</h4>
              <p className="text-gray-300 text-sm">
                TeaL;DR only requests the minimum permissions required for functionality. The bot never requests Administrator permission and cannot perform moderation actions, delete messages, or manage server settings.
              </p>
            </div>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/config/settings" className="text-[#5865F2] hover:underline">
                ← Bot Settings
              </Link>
              <Link href="/docs/config/retention" className="text-[#5865F2] hover:underline">
                Data Retention →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
