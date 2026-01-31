import Link from 'next/link';

export default function Terms() {
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
          <Link href="/" className="text-gray-400 hover:text-white transition-colors duration-300">
            ← Back to Home
          </Link>
        </div>
      </header>

      <main className="pt-32 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">Terms of Service</h1>
            <p className="text-gray-400 text-lg">Last updated: January 31, 2026</p>
          </div>

          <div className="p-6 bg-[#111111] border border-[#5865F2]/30 rounded-2xl mb-8">
            <p className="text-gray-300 leading-relaxed">
              By using TeaL;DR (&quot;the Bot&quot;), you agree to these Terms of Service. 
              Please read them carefully before adding the Bot to your Discord server.
            </p>
          </div>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">1. Acceptance of Terms</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                By inviting TeaL;DR to your Discord server or using any of its features, you acknowledge 
                that you have read, understood, and agree to be bound by these Terms of Service.
              </p>
              <p className="text-gray-300">
                If you do not agree to these terms, please do not use the Bot.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">2. Description of Service</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                TeaL;DR is a Discord bot that provides:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>AI-powered semantic search of server messages</li>
                <li>Conversation summaries and recaps</li>
                <li>Server analytics and statistics</li>
                <li>Export functionality for search results</li>
                <li>Interactive features like quizzes and yearly summaries</li>
                <li>Message indexing and storage for search purposes</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">3. Data Collection and Usage</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                The Bot collects and stores the following data:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4 mb-4">
                <li>Message content, author information, and timestamps</li>
                <li>Server IDs, channel IDs, and user IDs</li>
                <li>User interactions with the Bot (commands, feedback)</li>
                <li>Server configuration and settings</li>
              </ul>
              <p className="text-gray-300 mb-4">
                This data is used exclusively to:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Provide search and AI-powered features</li>
                <li>Generate summaries and analytics</li>
                <li>Improve Bot performance and functionality</li>
                <li>Maintain service quality and security</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">4. User Responsibilities</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">You agree to:</p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Use the Bot in compliance with Discord&apos;s Terms of Service</li>
                <li>Not attempt to abuse, exploit, or reverse-engineer the Bot</li>
                <li>Not use the Bot for illegal activities or harassment</li>
                <li>Ensure you have appropriate permissions before adding the Bot to a server</li>
                <li>Respect rate limits and not spam commands</li>
                <li>Not share or redistribute Bot data without permission</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">5. Data Retention</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                Messages are automatically deleted after 30 days by default (configurable by server admins).
              </p>
              <p className="text-gray-300 mb-4">
                Server administrators can:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Exclude specific channels from indexing</li>
                <li>Adjust message retention periods</li>
                <li>Request complete data deletion by removing the Bot</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">6. Service Availability</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                We strive to maintain 24/7 uptime, but we do not guarantee uninterrupted service.
              </p>
              <p className="text-gray-300">
                The Bot may be temporarily unavailable due to maintenance, updates, or technical issues. 
                We are not liable for any damages resulting from service interruptions.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">7. Limitation of Liability</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                TeaL;DR is provided &quot;as is&quot; without warranties of any kind. We are not responsible for:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Accuracy of AI-generated content or search results</li>
                <li>Data loss or corruption</li>
                <li>Misuse of the Bot by users</li>
                <li>Third-party service failures (Discord, hosting providers, AI APIs)</li>
                <li>Any damages arising from use of the Bot</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">8. Modifications to Service</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300">
                We reserve the right to modify, suspend, or discontinue the Bot at any time without notice. 
                We may also update these Terms of Service periodically. Continued use of the Bot after 
                changes constitutes acceptance of the new terms.
              </p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">9. Termination</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                We reserve the right to terminate or restrict access to the Bot for any user or server that:
              </p>
              <ul className="list-disc list-inside text-gray-300 space-y-2 ml-4">
                <li>Violates these Terms of Service</li>
                <li>Abuses or exploits the Bot</li>
                <li>Engages in illegal activities</li>
                <li>Causes harm to the service or other users</li>
              </ul>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-3xl font-bold mb-4">10. Contact Information</h2>
            <div className="p-6 bg-[#111111] border border-[#1a1a1a] rounded-xl">
              <p className="text-gray-300 mb-4">
                For questions, concerns, or data deletion requests, please contact us:
              </p>
              <ul className="list-none text-gray-300 space-y-2">
                <li>📧 Email: support@tealdr.com</li>
                <li>🐙 GitHub: <a href="https://github.com/limo-git/tea-bot" className="text-[#5865F2] hover:underline">github.com/limo-git/tea-bot</a></li>
              </ul>
            </div>
          </section>

          <div className="p-6 bg-[#5865F2]/10 border border-[#5865F2]/30 rounded-2xl mt-12">
            <p className="text-gray-300 text-center">
              By using TeaL;DR, you acknowledge that you have read and agree to these Terms of Service.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
