import Link from 'next/link';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a] border-b border-[#5865F2]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-lg font-bold tracking-tight">teal;dr</span>
          </Link>
          <Link href="/" className="text-[#a0a0a0] hover:text-[#5865F2] transition-colors duration-200">
            ← HOME
          </Link>
        </div>
      </header>

      <main className="pt-32 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">Privacy Policy</h1>
            <p className="text-gray-400 text-lg">Last updated: January 31, 2026</p>
          </div>

          <div className="p-6 bg-[#111111] border border-[#5865F2]/30 rounded-2xl mb-8">
            <p className="text-gray-300 leading-relaxed">
              Your privacy is important to us. This Privacy Policy explains how TeaL;DR (&quot;the Bot&quot;) 
              collects, uses, and protects your data when you use our Discord bot.
            </p>
          </div>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">1. Information We Collect</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Message Data</h3>
              <p className="text-gray-300 mb-4">
                When the Bot is active in your server, we collect:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4 mb-6">
                <li>Message content and attachments</li>
                <li>Author username and user ID</li>
                <li>Channel ID and server ID</li>
                <li>Message timestamps</li>
                <li>Thread information (if applicable)</li>
              </ul>

              <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Usage Data</h3>
              <p className="text-gray-300 mb-4">
                We collect information about how you interact with the Bot:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4 mb-6">
                <li>Commands used and their parameters</li>
                <li>Search queries and filters</li>
                <li>Feedback reactions (👍/👎)</li>
                <li>Quiz participation and scores</li>
                <li>Export requests</li>
              </ul>

              <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Server Configuration</h3>
              <p className="text-gray-300 mb-4">
                Server administrators can configure settings, which we store:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Excluded channels</li>
                <li>Message retention periods</li>
                <li>Custom bot personality settings</li>
                <li>Permission configurations</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">2. How We Use Your Information</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                We use collected data to:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li><strong className="text-white">Provide search functionality:</strong> Index messages for semantic search and AI-powered queries</li>
                <li><strong className="text-white">Generate AI responses:</strong> Create summaries, recaps, and answer questions about server history</li>
                <li><strong className="text-white">Create analytics:</strong> Generate server statistics and user activity insights</li>
                <li><strong className="text-white">Enable features:</strong> Power quizzes, yearly wrapped summaries, and time machine lookbacks</li>
                <li><strong className="text-white">Improve service:</strong> Analyze usage patterns to enhance Bot performance and features</li>
                <li><strong className="text-white">Maintain security:</strong> Detect and prevent abuse or misuse of the Bot</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">3. Data Storage and Security</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Where We Store Data</h3>
              <p className="text-gray-300 mb-4">
                Your data is stored securely using:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4 mb-6">
                <li><strong className="text-white">Supabase (PostgreSQL):</strong> Message content, metadata, and embeddings</li>
                <li><strong className="text-white">In-memory cache:</strong> Temporary caching for performance (cleared regularly)</li>
                <li><strong className="text-white">Render.com:</strong> Bot hosting and processing</li>
              </ul>

              <h3 className="text-xl font-semibold text-[#5865F2] mb-3">Security Measures</h3>
              <p className="text-gray-300 mb-4">
                We implement industry-standard security practices:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Encrypted data transmission (HTTPS/TLS)</li>
                <li>Secure database access with authentication</li>
                <li>Multi-server data isolation (your data is never mixed with other servers)</li>
                <li>Regular security updates and monitoring</li>
                <li>Limited access to production data</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">4. Data Retention</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                <strong className="text-white">Automatic Deletion:</strong> Messages are automatically deleted after 30 days by default. 
                Server administrators can adjust this period (7-90 days).
              </p>
              <p className="text-gray-300 mb-4">
                <strong className="text-white">Manual Deletion:</strong> Server admins can exclude channels from indexing at any time.
              </p>
              <p className="text-gray-300">
                <strong className="text-white">Complete Removal:</strong> Removing the Bot from your server will stop new data collection. 
                Existing data will be automatically purged within 30 days.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">5. Data Sharing</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                We do NOT sell, rent, or trade your data. We only share data with:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4 mb-6">
                <li><strong className="text-white">Google Gemini AI:</strong> Message content is sent to generate embeddings and AI responses (processed, not stored by Google)</li>
                <li><strong className="text-white">Service providers:</strong> Supabase (database), Render (hosting) - only as necessary to operate the Bot</li>
                <li><strong className="text-white">Legal requirements:</strong> If required by law or to protect our rights</li>
              </ul>
              <p className="text-gray-300">
                Your data remains isolated to your server and is never shared with other Discord servers or users.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">6. Third-Party Services</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                The Bot integrates with third-party services:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li><strong className="text-white">Discord:</strong> Subject to Discord&apos;s Privacy Policy</li>
                <li><strong className="text-white">Google Gemini AI:</strong> Subject to Google&apos;s Privacy Policy</li>
                <li><strong className="text-white">Supabase:</strong> Subject to Supabase&apos;s Privacy Policy</li>
              </ul>
              <p className="text-gray-300 mt-4">
                We recommend reviewing these third-party privacy policies.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">7. Your Rights</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                You have the right to:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li><strong className="text-white">Access:</strong> Request a copy of your data</li>
                <li><strong className="text-white">Deletion:</strong> Request deletion of your data</li>
                <li><strong className="text-white">Correction:</strong> Request correction of inaccurate data</li>
                <li><strong className="text-white">Opt-out:</strong> Exclude specific channels or remove the Bot entirely</li>
                <li><strong className="text-white">Portability:</strong> Export your data using the <code className="text-[#5865F2]">/export</code> command</li>
              </ul>
              <p className="text-gray-300 mt-4">
                To exercise these rights, contact us at support@tealdr.com or use the Bot&apos;s built-in commands.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">8. Children&apos;s Privacy</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300">
                The Bot is not intended for users under 13 years old (or the minimum age required in your country). 
                We do not knowingly collect data from children. If you believe we have collected data from a child, 
                please contact us immediately.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">9. Changes to This Policy</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300">
                We may update this Privacy Policy from time to time. Changes will be posted on this page with 
                an updated &quot;Last updated&quot; date. Continued use of the Bot after changes constitutes acceptance 
                of the updated policy.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">10. Contact Us</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                For privacy-related questions, data requests, or concerns:
              </p>
              <ul className="list-none text-gray-300 space-y-2">
                <li>📧 Email: support@tealdr.com</li>
                <li>🐙 GitHub: <a href="https://github.com/limo-git/tea-bot" className="text-[#5865F2] hover:underline">github.com/limo-git/tea-bot</a></li>
              </ul>
            </div>
          </section>

          <div className="p-6 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-2xl mt-12">
            <p className="text-gray-300 text-center">
              We are committed to protecting your privacy and being transparent about our data practices.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
