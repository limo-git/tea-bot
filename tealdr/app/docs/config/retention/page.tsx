import Link from 'next/link';

export default function DataRetention() {
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
                <li><Link href="/docs/config/permissions" className="text-gray-400 hover:text-white transition-colors">Permissions</Link></li>
                <li><Link href="/docs/config/retention" className="text-[#5865F2] hover:text-white transition-colors">Data Retention</Link></li>
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
            <h1 className="text-4xl font-bold mb-4">Data Retention</h1>
            <p className="text-xl text-gray-400">
              Understanding how TeaL;DR stores and manages your server&apos;s data.
            </p>
          </div>

          <div className="prose prose-invert max-w-none">
            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Overview</h2>
              <p className="text-gray-300 mb-4">
                TeaL;DR automatically manages data retention to balance searchability with privacy and storage efficiency. All retention settings are configurable by server administrators.
              </p>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Default Retention Policy</h3>
                <ul className="space-y-3 text-gray-300 text-sm">
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">•</span>
                    <div>
                      <strong>Messages:</strong> Automatically deleted after 30 days
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">•</span>
                    <div>
                      <strong>Embeddings:</strong> Deleted with associated messages
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">•</span>
                    <div>
                      <strong>Analytics:</strong> Aggregated data retained for 90 days
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#5865F2] mt-1">•</span>
                    <div>
                      <strong>Configuration:</strong> Retained until bot removal
                    </div>
                  </li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Configuring Retention Period</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Set Custom Retention Period</h3>
                <p className="text-gray-300 text-sm mb-4">
                  Administrators can adjust the message retention period between 7 and 90 days:
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm mb-4">
                  /settings action: Set Retention Period days: 60
                </code>
                <div className="space-y-2 text-sm text-gray-300">
                  <p><strong>Minimum:</strong> 7 days</p>
                  <p><strong>Maximum:</strong> 90 days</p>
                  <p><strong>Default:</strong> 30 days</p>
                </div>
              </div>

              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">View Current Retention</h3>
                <p className="text-gray-300 text-sm mb-4">
                  Check your current retention period setting:
                </p>
                <code className="block text-[#5865F2] bg-[#0a0a0a] px-4 py-3 rounded font-mono text-sm">
                  /settings action: View Retention Period
                </code>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">7-14 Days</h4>
                  <p className="text-gray-400 text-sm mb-2">Short-term retention</p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Recent discussions only</li>
                    <li>• Minimal storage</li>
                    <li>• High privacy</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#5865F2]/30 rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">30 Days</h4>
                  <p className="text-gray-400 text-sm mb-2">Recommended (Default)</p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Balanced approach</li>
                    <li>• Good searchability</li>
                    <li>• Reasonable storage</li>
                  </ul>
                </div>

                <div className="p-4 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h4 className="text-md font-semibold text-[#5865F2] mb-2">60-90 Days</h4>
                  <p className="text-gray-400 text-sm mb-2">Long-term archival</p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• Extended history</li>
                    <li>• More storage needed</li>
                    <li>• Comprehensive search</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">What Gets Stored</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Message Data</h3>
                  <p className="text-gray-300 text-sm mb-3">For each indexed message, we store:</p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li><strong>Content:</strong> Full message text</li>
                    <li><strong>Metadata:</strong> Author ID, channel ID, timestamp</li>
                    <li><strong>Embeddings:</strong> AI-generated semantic vectors (768 dimensions)</li>
                    <li><strong>Context:</strong> Thread information, reply references</li>
                  </ul>
                  <p className="text-gray-400 text-xs mt-3">
                    <strong>Storage per message:</strong> ~2-5 KB (text + embeddings)
                  </p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Analytics Data</h3>
                  <p className="text-gray-300 text-sm mb-3">Aggregated statistics stored separately:</p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Message counts per user/channel</li>
                    <li>Activity patterns and trends</li>
                    <li>Topic distributions</li>
                    <li>Engagement metrics</li>
                  </ul>
                  <p className="text-gray-400 text-xs mt-3">
                    <strong>Note:</strong> Analytics are anonymized and aggregated
                  </p>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Configuration Data</h3>
                  <p className="text-gray-300 text-sm mb-3">Server settings and preferences:</p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Excluded channels list</li>
                    <li>Retention period setting</li>
                    <li>Bot personality preference</li>
                    <li>Permission configurations</li>
                  </ul>
                  <p className="text-gray-400 text-xs mt-3">
                    <strong>Retention:</strong> Kept until bot is removed from server
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Automatic Deletion</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">How It Works</h3>
                <ol className="list-decimal list-inside text-gray-300 text-sm space-y-3">
                  <li>
                    <strong>Daily Cleanup:</strong> Bot runs automated cleanup every 24 hours
                  </li>
                  <li>
                    <strong>Age Check:</strong> Messages older than retention period are identified
                  </li>
                  <li>
                    <strong>Deletion:</strong> Messages and embeddings are permanently deleted
                  </li>
                  <li>
                    <strong>Analytics Update:</strong> Aggregated stats are updated
                  </li>
                </ol>
              </div>

              <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg">
                <h4 className="text-sm font-semibold mb-2">⏰ Timing</h4>
                <p className="text-gray-300 text-sm">
                  Automatic deletion runs at 00:00 UTC daily. Messages are deleted based on their creation timestamp, not when they were indexed.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Manual Data Management</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Clear Channel Data</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Delete all indexed data from a specific channel:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm mb-3">
                    /settings action: Clear Channel Data channel: #old-channel
                  </code>
                  <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-gray-300">
                    <strong>⚠️ Warning:</strong> This action is irreversible. All search history for this channel will be permanently deleted.
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-red-500/30 rounded-xl">
                  <h3 className="text-lg font-semibold text-red-400 mb-3">Clear All Server Data</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Delete all indexed data for your entire server:
                  </p>
                  <code className="block text-[#5865F2] bg-[#0a0a0a] px-3 py-2 rounded font-mono text-sm mb-3">
                    /settings action: Clear All Data confirm: yes
                  </code>
                  <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-gray-300">
                    <strong>⚠️ Critical:</strong> This deletes all messages, embeddings, analytics, and configuration. Requires explicit confirmation.
                  </div>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Bot Removal</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    When you remove the bot from your server:
                  </p>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>New message indexing stops immediately</li>
                    <li>Existing data is retained for 30 days</li>
                    <li>After 30 days, all data is permanently deleted</li>
                    <li>Re-adding the bot within 30 days restores configuration</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Storage Estimates</h2>
              
              <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl mb-6">
                <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Typical Server Storage</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b border-[#1a1a1a]">
                      <tr className="text-left">
                        <th className="py-3 text-gray-400">Server Size</th>
                        <th className="py-3 text-gray-400">Messages/Day</th>
                        <th className="py-3 text-gray-400">30-Day Storage</th>
                        <th className="py-3 text-gray-400">90-Day Storage</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-300">
                      <tr className="border-b border-[#1a1a1a]">
                        <td className="py-3">Small</td>
                        <td className="py-3">100-500</td>
                        <td className="py-3">~50-250 MB</td>
                        <td className="py-3">~150-750 MB</td>
                      </tr>
                      <tr className="border-b border-[#1a1a1a]">
                        <td className="py-3">Medium</td>
                        <td className="py-3">500-2000</td>
                        <td className="py-3">~250 MB-1 GB</td>
                        <td className="py-3">~750 MB-3 GB</td>
                      </tr>
                      <tr className="border-b border-[#1a1a1a]">
                        <td className="py-3">Large</td>
                        <td className="py-3">2000-10000</td>
                        <td className="py-3">~1-5 GB</td>
                        <td className="py-3">~3-15 GB</td>
                      </tr>
                      <tr>
                        <td className="py-3">Very Large</td>
                        <td className="py-3">10000+</td>
                        <td className="py-3">~5+ GB</td>
                        <td className="py-3">~15+ GB</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-gray-400 text-xs mt-3">
                  <strong>Note:</strong> Estimates include message content, embeddings, and metadata. Actual storage may vary based on message length and attachment frequency.
                </p>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold mb-4">Retention Best Practices</h2>
              
              <div className="space-y-4">
                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Choosing the Right Period</h3>
                  <ul className="space-y-3 text-gray-300 text-sm">
                    <li className="flex items-start gap-3">
                      <span className="text-[#5865F2] mt-1">•</span>
                      <div>
                        <strong>Active Servers:</strong> 30 days provides good balance for most use cases
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-[#5865F2] mt-1">•</span>
                      <div>
                        <strong>Archival Needs:</strong> 60-90 days for servers requiring longer history
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-[#5865F2] mt-1">•</span>
                      <div>
                        <strong>Privacy Focus:</strong> 7-14 days for maximum privacy and minimal storage
                      </div>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-[#5865F2] mt-1">•</span>
                      <div>
                        <strong>High Traffic:</strong> Shorter periods help manage storage on very active servers
                      </div>
                    </li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Regular Maintenance</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Review retention settings quarterly</li>
                    <li>Monitor storage usage with <code className="text-[#5865F2] bg-[#0a0a0a] px-2 py-1 rounded">/stats</code></li>
                    <li>Adjust based on server activity patterns</li>
                    <li>Clear old channel data when channels are archived</li>
                    <li>Document retention policy in server rules</li>
                  </ul>
                </div>

                <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
                  <h3 className="text-lg font-semibold text-[#5865F2] mb-3">Compliance Considerations</h3>
                  <ul className="list-disc list-inside text-gray-300 text-sm space-y-2">
                    <li>Ensure retention period complies with your privacy policy</li>
                    <li>Consider GDPR/data protection requirements</li>
                    <li>Document data retention in Terms of Service</li>
                    <li>Provide clear deletion procedures for users</li>
                  </ul>
                </div>
              </div>
            </section>

            <div className="p-4 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-lg mb-6">
              <h4 className="text-sm font-semibold mb-2">🔒 Privacy Guarantee</h4>
              <p className="text-gray-300 text-sm">
                All data is isolated per server. Your server&apos;s data is never shared with other servers or used for training AI models. Data deletion is permanent and cannot be recovered.
              </p>
            </div>

            <div className="flex items-center justify-between p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <Link href="/docs/config/permissions" className="text-[#5865F2] hover:underline">
                ← Permissions
              </Link>
              <Link href="/docs/advanced/architecture" className="text-[#5865F2] hover:underline">
                Architecture →
              </Link>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
