'use client';

import { useState } from 'react';

interface Command {
  name: string;
  description: string;
  parameters: { name: string; type: string; required: boolean; options?: string[] }[];
  example: string;
  response: string;
}

const commands: Record<string, Command> = {
  ask: {
    name: '/ask',
    description: 'Search through your server history with natural language',
    parameters: [
      { name: 'query', type: 'text', required: true }
    ],
    example: 'what did @john say about the API yesterday?',
    response: '🔍 **Search Results**\n\nFound 3 relevant messages from @john about the API:\n\n**1.** "The new API endpoint is working great!"\n   _Posted in #development - Yesterday at 2:34 PM_\n\n**2.** "We should update the documentation"\n   _Posted in #development - Yesterday at 3:15 PM_\n\n**3.** "Rate limiting is set to 100 req/min"\n   _Posted in #development - Yesterday at 4:02 PM_'
  },
  recap: {
    name: '/recap',
    description: 'Get AI-generated summaries of conversations',
    parameters: [
      { name: 'period', type: 'select', required: true, options: ['Last 24 hours', 'Last 7 days', 'Last 30 days'] },
      { name: 'channel', type: 'text', required: false }
    ],
    example: 'Last 7 days in #general',
    response: '📝 **Summary of #general (Last 7 days)**\n\n**Main Topics Discussed:**\n• New feature deployment scheduled for Friday\n• Bug fixes in authentication system\n• Team meeting notes and action items\n• Q1 planning and roadmap discussion\n\n**Most Active Members:** @alice (127 messages), @bob (94 messages), @charlie (78 messages)\n\n**Key Decisions:**\n✓ Approved new UI design\n✓ Migrating to PostgreSQL next month\n✓ Weekly standups moved to Tuesdays'
  },
  stats: {
    name: '/stats',
    description: 'View comprehensive server and user activity statistics',
    parameters: [
      { name: 'scope', type: 'select', required: true, options: ['Server Statistics', 'User Statistics', 'Channel Statistics'] }
    ],
    example: 'Server Statistics',
    response: '📊 **Server Statistics**\n\n**Overview:**\n• Total Messages: 15,234\n• Active Users: 87\n• Total Channels: 24\n• Server Age: 247 days\n\n**Activity:**\n📝 Most Active Channel: #general (3,421 messages)\n👤 Top Contributor: @alice (1,847 messages)\n⏰ Peak Activity: 2-4 PM UTC\n📈 Growth: +12% this month\n\n**Trending Topics:**\n🔥 API development\n🔥 deployment\n🔥 testing'
  },
  export: {
    name: '/export',
    description: 'Export search results to various formats',
    parameters: [
      { name: 'query', type: 'text', required: true },
      { name: 'format', type: 'select', required: true, options: ['CSV', 'JSON', 'Markdown', 'TXT'] }
    ],
    example: 'project discussions as CSV',
    response: '📁 **Export Completed Successfully!**\n\n**File Details:**\n• Filename: project_discussions.csv\n• Records: 156 messages\n• Size: 42 KB\n• Format: CSV\n\n**Contents:**\n✓ Message content\n✓ Author information\n✓ Timestamps\n✓ Channel references\n\n🔗 Download link expires in 24 hours.\n\n_Click the link below to download your export._'
  },
  quiz: {
    name: '/quiz',
    description: 'Create a Kahoot-style trivia game from server history',
    parameters: [
      { name: 'num_questions', type: 'number', required: true },
      { name: 'time_period', type: 'select', required: false, options: ['Last 7 days', 'Last 30 days', 'All time'] }
    ],
    example: '5 questions from Last 30 days',
    response: '🎮 **Quiz Created!**\n\n**Quiz Details:**\n• Questions: 5\n• Time per question: 30 seconds\n• Category: Server History\n• Difficulty: Mixed\n\n**Sample Questions:**\n1. What feature did @alice propose last week?\n2. Which database did the team choose?\n3. When is the next deployment scheduled?\n\n⏱️ Starting in 10 seconds...\n🎯 React with 🎯 to join the game!'
  },
  wrapped: {
    name: '/wrapped',
    description: 'Generate a Spotify Wrapped-style yearly summary',
    parameters: [
      { name: 'year', type: 'number', required: true }
    ],
    example: '2025',
    response: '🎊 **Your 2025 Wrapped!**\n\n**Your Year in Review:**\n🏆 Top Contributor: @alice (2,341 messages)\n📅 Most Active Month: March (487 messages)\n💬 Favorite Channel: #general (1,234 messages)\n⏰ Peak Hour: 3 PM UTC\n\n**Top Topics:**\n1. 🔧 coding (342 mentions)\n2. 🎨 design (198 mentions)\n3. 📊 meetings (156 mentions)\n\n**Milestones:**\n✨ You sent 15,234 messages this year!\n🚀 That\'s 42 messages per day!\n🎉 You were active on 287 days!'
  },
  timemachine: {
    name: '/timemachine',
    description: 'See what happened on this day in previous years',
    parameters: [
      { name: 'date', type: 'text', required: true }
    ],
    example: '01-31',
    response: '⏰ **On This Day (January 31)**\n\n**2024:**\n🚀 Project launch announcement\n📝 First client demo completed\n🎉 Team celebration for milestone\n\n**2023:**\n🎊 Reached 1000 server members\n💼 New partnership announced\n🏆 Won community award\n\n**2022:**\n🤖 First bot integration\n📱 Mobile app beta released\n\n**3 years of memories!** 🎉'
  },
  'request-summary': {
    name: '/request-summary',
    description: 'Get personalized summaries delivered to your DMs or email',
    parameters: [
      { name: 'time_period', type: 'select', required: true, options: ['Last 24 hours', 'Last 7 days', 'Last 30 days'] },
      { name: 'delivery', type: 'select', required: true, options: ['Send to DM', 'Send to Email'] }
    ],
    example: 'Last 7 days via DM',
    response: '✅ **Summary Sent to Your DMs!**\n\nCheck your direct messages for a personalized recap of the last 7 days.\n\n**Summary Includes:**\n• Key topics and discussions\n• Important announcements\n• Action items and decisions\n• Mentions of you\n\n📬 The summary has been delivered to your DMs.\n\n_Use /dm-settings to configure automatic summaries._'
  },
  'bug-summary': {
    name: '/bug-summary',
    description: 'View recent bug discussions and dependency updates',
    parameters: [
      { name: 'days', type: 'number', required: false }
    ],
    example: '7 days',
    response: '🐛 **Bug Summary - Last 7 Days**\n\n**📊 Overview:**\n• Total: 5 bugs tracked\n• Resolved: 3\n• Unresolved: 2\n• Critical: 0\n\n**✅ Recently Resolved:**\n• **React 18.2.0:** Fixed hydration error in production\n• **Next.js 14:** Resolved build issue with middleware\n• **TypeScript:** Fixed type inference bug\n\n**⚠️ Unresolved Issues:**\n• **PostgreSQL:** Connection pool timeout (medium)\n• **Redis:** Cache invalidation issue (low)\n\n_Use /dm-settings to enable automatic bug alerts._'
  },
  'dm-settings': {
    name: '/dm-settings',
    description: 'Manage your DM summary and email preferences',
    parameters: [
      { name: 'action', type: 'select', required: true, options: ['View Settings', 'Toggle DM Summaries', 'Toggle Email Summaries', 'Set Email', 'Set Frequency', 'Toggle Bug Alerts'] },
      { name: 'value', type: 'text', required: false }
    ],
    example: 'Toggle DM Summaries',
    response: '✅ **DM Summaries Enabled**\n\n**Your Current Settings:**\n📬 DM Summaries: ✅ Enabled\n📧 Email Summaries: ❌ Disabled\n⏰ Frequency: Weekly\n🐛 Bug Alerts: ✅ Enabled\n\nYou\'ll now receive personalized summaries in your DMs every week.\n\n_Use /summary-topics to filter by topics._\n_Use /summary-servers to select servers._'
  },
  'summary-topics': {
    name: '/summary-topics',
    description: 'Choose which topics you want summaries about',
    parameters: [
      { name: 'action', type: 'select', required: true, options: ['View Topics', 'Add Topic', 'Remove Topic', 'Clear All Topics'] },
      { name: 'topic', type: 'text', required: false }
    ],
    example: 'Add Topic: bug fixes',
    response: '✅ **Added Topic: bug fixes**\n\nYou\'ll now receive summaries about this topic from this server.\n\n**Your Active Topics:**\n• bug fixes\n• feature requests\n• deployment\n• security\n\n**How it works:**\nSummaries will only include messages that mention these topics, helping you stay focused on what matters most.\n\n_Use /summary-topics action: View Topics to see all your filters._'
  },
  'summary-servers': {
    name: '/summary-servers',
    description: 'Select which servers send you summaries',
    parameters: [
      { name: 'action', type: 'select', required: true, options: ['View Enabled Servers', 'Enable This Server', 'Disable This Server'] }
    ],
    example: 'Enable This Server',
    response: '✅ **Enabled Summaries from My Server**\n\nYou\'ll now receive summaries from this server in your DMs.\n\n**Your Enabled Servers:**\n✅ My Server\n✅ Development Team\n✅ Community Hub\n❌ Test Server\n\n**Next Summary:**\nBased on your weekly frequency, your next summary will be sent on Friday at 9:00 AM.\n\n_Use /dm-settings to change frequency._'
  },
  settings: {
    name: '/settings',
    description: 'Configure bot behavior and permissions (Admin only)',
    parameters: [
      { name: 'action', type: 'select', required: true, options: ['Exclude Channel', 'Include Channel', 'Set Retention', 'View Settings'] },
      { name: 'channel', type: 'text', required: false }
    ],
    example: 'Exclude Channel: #private',
    response: '⚙️ **Settings Updated Successfully!**\n\n**Changes Applied:**\n✓ Channel #private excluded from indexing\n✓ Existing messages will not be searchable\n✓ New messages will be ignored\n\n**Current Server Settings:**\n📝 Indexed Channels: 18/24\n🔒 Excluded Channels: #private, #admin, #mod-chat\n⏰ Retention Period: 30 days\n🤖 Bot Personality: Professional\n\n_Only server administrators can modify these settings._'
  },
  customize: {
    name: '/customize',
    description: 'Set custom bot personality (Admin only)',
    parameters: [
      { name: 'persona', type: 'select', required: true, options: ['Professional', 'Casual', 'Friendly', 'Technical'] }
    ],
    example: 'Professional',
    response: '🎨 **Bot Personality Updated!**\n\n**New Personality:** Professional\n\n**What this means:**\n• Formal and concise responses\n• Technical terminology when appropriate\n• Structured formatting\n• Business-focused tone\n\n**Example Response Style:**\n_"The search query has been processed. 3 relevant results were identified based on semantic analysis of your request."_\n\n✅ All future bot responses will use this personality.\n\n_Only server administrators can customize the bot personality._'
  },
  clear: {
    name: '/clear',
    description: 'Clear your conversation context with the bot',
    parameters: [],
    example: '',
    response: '🗑️ **Context Cleared Successfully!**\n\nYour conversation history with the bot has been reset.\n\n**What was cleared:**\n✓ Previous queries\n✓ Search context\n✓ Conversation memory\n\n**What remains:**\n✓ Your user preferences\n✓ DM settings\n✓ Topic filters\n✓ Server settings\n\nYou can now start fresh with new queries!'
  },
  help: {
    name: '/help',
    description: 'Show all available commands and tips',
    parameters: [],
    example: '',
    response: '❓ **TeaL;DR Help Center**\n\n**Available Commands:**\n🔍 `/ask` - Search server history\n📝 `/recap` - Get conversation summaries\n📊 `/stats` - View server statistics\n📤 `/export` - Export search results\n🎮 `/quiz` - Create trivia games\n🎊 `/wrapped` - Yearly summaries\n⏰ `/timemachine` - Historical events\n📬 `/request-summary` - Get DM summaries\n🐛 `/bug-summary` - Bug tracking\n⚙️ `/dm-settings` - Manage preferences\n🏷️ `/summary-topics` - Filter topics\n🌐 `/summary-servers` - Select servers\n\n**Quick Tips:**\n💡 Use natural language in /ask queries\n💡 Set up DM summaries for daily updates\n💡 Filter by topics to reduce noise\n\n📚 Visit our docs for detailed guides!'
  }
};

export default function InteractiveDemo() {
  const [selectedCommand, setSelectedCommand] = useState('ask');
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [showResponse, setShowResponse] = useState(false);

  const currentCommand = commands[selectedCommand];

  const handleCommandChange = (cmd: string) => {
    setSelectedCommand(cmd);
    setParamValues({});
    setShowResponse(false);
  };

  const handleParamChange = (paramName: string, value: string) => {
    setParamValues(prev => ({ ...prev, [paramName]: value }));
  };

  const handleExecute = () => {
    setShowResponse(true);
  };

  const buildCommandString = () => {
    let cmd = currentCommand.name;
    const params = Object.entries(paramValues)
      .filter(([_, value]) => value)
      .map(([key, value]) => `${key}: ${value}`)
      .join(' ');
    
    return params ? `${cmd} ${params}` : cmd;
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Panel - Command Builder */}
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold mb-4">Try a Command</h3>
            <p className="text-gray-400 mb-6">Select a command and fill in the parameters to see how it works</p>
          </div>

          {/* Command Selector */}
          <div>
            <label className="block text-sm font-semibold mb-3 text-gray-300">Select Command</label>
            <div className="relative">
              <select
                value={selectedCommand}
                onChange={(e) => handleCommandChange(e.target.value)}
                className="w-full px-4 py-3 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:border-[#5865F2] transition-colors appearance-none pr-10"
              >
                {Object.keys(commands).map(cmd => (
                  <option key={cmd} value={cmd}>{commands[cmd].name}</option>
                ))}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Command Description */}
          <div className="p-4 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg">
            <p className="text-sm text-gray-400">{currentCommand.description}</p>
          </div>

          {/* Parameters */}
          {currentCommand.parameters.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-300">Parameters</h4>
              {currentCommand.parameters.map(param => (
                <div key={param.name}>
                  <label className="block text-sm mb-2 text-gray-400">
                    {param.name} {param.required && <span className="text-red-400">*</span>}
                  </label>
                  {param.type === 'select' && param.options ? (
                    <div className="relative">
                      <select
                        value={paramValues[param.name] || ''}
                        onChange={(e) => handleParamChange(param.name, e.target.value)}
                        className="w-full px-4 py-2 bg-[#111111] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:border-[#5865F2] transition-colors appearance-none pr-10"
                      >
                        <option value="">Select {param.name}</option>
                        {param.options.map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  ) : param.type === 'number' ? (
                    <input
                      type="number"
                      value={paramValues[param.name] || ''}
                      onChange={(e) => handleParamChange(param.name, e.target.value)}
                      placeholder={`Enter ${param.name}`}
                      className="w-full px-4 py-2 bg-[#111111] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:border-[#5865F2] transition-colors"
                    />
                  ) : (
                    <input
                      type="text"
                      value={paramValues[param.name] || ''}
                      onChange={(e) => handleParamChange(param.name, e.target.value)}
                      placeholder={currentCommand.example}
                      className="w-full px-4 py-2 bg-[#111111] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:border-[#5865F2] transition-colors"
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Command Preview */}
          <div className="p-4 bg-[#0a0a0a] border border-[#2a2a2a] rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Command Preview:</p>
            <code className="text-[#5865F2] font-mono text-sm">{buildCommandString()}</code>
          </div>

          {/* Execute Button */}
          <button
            onClick={handleExecute}
            className="w-full px-6 py-3 bg-[#5865F2] rounded-lg font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-[#5865F2]/50 hover:scale-105"
          >
            Execute Command
          </button>
        </div>

        {/* Right Panel - Response Display */}
        <div className="lg:sticky lg:top-8 h-fit">
          <div className="bg-[#111111] border border-[#2a2a2a] rounded-lg p-6 min-h-[560px]">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-[#2a2a2a]">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-2 text-sm text-gray-500 font-mono">TeaL;DR Response</span>
            </div>

            {showResponse ? (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-start gap-3">
                  <img 
                    src="/tea-bot-pfp.png" 
                    alt="TeaL;DR Bot" 
                    className="w-8 h-8 rounded-full flex-shrink-0"
                  />
                  <div className="flex-1">
                    <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
                      <div className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed response-content">
                        {currentCommand.response.split('\n').map((line, idx) => {
                          // Handle bold text **text**
                          if (line.includes('**')) {
                            const parts = line.split(/(\*\*.*?\*\*)/g);
                            return (
                              <div key={idx}>
                                {parts.map((part, i) => {
                                  if (part.startsWith('**') && part.endsWith('**')) {
                                    return <strong key={i} className="font-bold text-white">{part.slice(2, -2)}</strong>;
                                  }
                                  return <span key={i}>{part}</span>;
                                })}
                              </div>
                            );
                          }
                          // Handle italic text _text_
                          if (line.includes('_') && !line.startsWith('_')) {
                            const parts = line.split(/(_.*?_)/g);
                            return (
                              <div key={idx}>
                                {parts.map((part, i) => {
                                  if (part.startsWith('_') && part.endsWith('_')) {
                                    return <em key={i} className="italic text-gray-400">{part.slice(1, -1)}</em>;
                                  }
                                  return <span key={i}>{part}</span>;
                                })}
                              </div>
                            );
                          }
                          // Regular line
                          return <div key={idx}>{line || '\u00A0'}</div>;
                        })}
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">Just now</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-[#1a1a1a] flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <p className="text-gray-500">Execute a command to see the response</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
