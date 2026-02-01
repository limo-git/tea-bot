from database.supabase_client import supabase_client
from utils.logger import get_logger
from datetime import datetime
import re

logger = get_logger(__name__)

class BugTracker:
    """Tracks bug discussions and dependency updates in server conversations"""
    
    # Keywords that indicate bug/dependency discussions
    BUG_KEYWORDS = [
        'bug', 'error', 'issue', 'broken', 'fix', 'crash', 'dependency',
        'vulnerability', 'security', 'patch', 'update', 'deprecated',
        'breaking change', 'regression', 'hotfix'
    ]
    
    DEPENDENCY_PATTERNS = [
        r'npm\s+(?:install|update|upgrade)\s+([a-z0-9@\-/]+)',
        r'pip\s+install\s+([a-z0-9\-_]+)',
        r'yarn\s+add\s+([a-z0-9@\-/]+)',
        r'package[:\s]+([a-z0-9@\-/]+)',
        r'library[:\s]+([a-z0-9@\-/]+)'
    ]
    
    @staticmethod
    def is_bug_discussion(message_content: str) -> bool:
        """Check if message is about a bug or dependency issue"""
        content_lower = message_content.lower()
        return any(keyword in content_lower for keyword in BugTracker.BUG_KEYWORDS)
    
    @staticmethod
    def extract_dependency_name(message_content: str) -> str:
        """Extract dependency name from message"""
        for pattern in BugTracker.DEPENDENCY_PATTERNS:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def determine_severity(message_content: str) -> str:
        """Determine bug severity from message content"""
        content_lower = message_content.lower()
        
        if any(word in content_lower for word in ['critical', 'severe', 'security', 'vulnerability', 'crash']):
            return 'critical'
        elif any(word in content_lower for word in ['high', 'major', 'breaking']):
            return 'high'
        elif any(word in content_lower for word in ['medium', 'moderate']):
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def track_bug_discussion(server_id: int, channel_id: int, message_id: int, 
                            message_content: str) -> bool:
        """Track a bug discussion in the database"""
        try:
            dependency = BugTracker.extract_dependency_name(message_content)
            severity = BugTracker.determine_severity(message_content)
            
            bug_data = {
                'server_id': server_id,
                'channel_id': channel_id,
                'message_id': message_id,
                'dependency_name': dependency,
                'bug_description': message_content[:500],  # Truncate to 500 chars
                'severity': severity,
                'resolved': False
            }
            
            result = supabase_client.client.table('bug_discussions').insert(bug_data).execute()
            logger.info(f"Tracked bug discussion in server {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking bug discussion: {e}")
            return False
    
    @staticmethod
    def mark_bug_resolved(bug_id: int, resolution: str) -> bool:
        """Mark a bug as resolved with resolution details"""
        try:
            result = supabase_client.client.table('bug_discussions').update({
                'resolved': True,
                'resolution': resolution,
                'resolved_at': datetime.utcnow().isoformat()
            }).eq('id', bug_id).execute()
            
            logger.info(f"Marked bug {bug_id} as resolved")
            return True
            
        except Exception as e:
            logger.error(f"Error marking bug as resolved: {e}")
            return False
    
    @staticmethod
    def get_recent_bugs(server_id: int, days: int = 7, resolved: bool = None) -> list:
        """Get recent bug discussions for a server"""
        try:
            query = supabase_client.client.table('bug_discussions').select('*').eq('server_id', server_id)
            
            if resolved is not None:
                query = query.eq('resolved', resolved)
            
            # Get bugs from last N days
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            query = query.gte('created_at', cutoff_date.isoformat())
            query = query.order('created_at', desc=True)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting recent bugs: {e}")
            return []
    
    @staticmethod
    def generate_bug_summary(server_id: int, days: int = 7) -> dict:
        """Generate a summary of recent bugs and their resolutions"""
        try:
            all_bugs = BugTracker.get_recent_bugs(server_id, days)
            resolved_bugs = [b for b in all_bugs if b['resolved']]
            unresolved_bugs = [b for b in all_bugs if not b['resolved']]
            
            summary = {
                'total_bugs': len(all_bugs),
                'resolved': len(resolved_bugs),
                'unresolved': len(unresolved_bugs),
                'critical_bugs': len([b for b in all_bugs if b['severity'] == 'critical']),
                'bugs': all_bugs,
                'resolved_bugs': resolved_bugs,
                'unresolved_bugs': unresolved_bugs
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating bug summary: {e}")
            return None

bug_tracker = BugTracker()
