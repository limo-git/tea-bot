"""
Private Session Manager
Allows admins to temporarily disable message indexing for specific channels.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from utils.logger import get_logger

logger = get_logger(__name__)


class PrivateSessionManager:
    """Manages private sessions where message indexing is disabled."""
    
    def __init__(self):
        # Structure: {channel_id: {'end_time': datetime, 'started_by': user_id, 'server_id': server_id}}
        self._active_sessions: Dict[int, Dict] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def start_session(self, channel_id: int, server_id: int, duration_minutes: int, started_by: int) -> datetime:
        """
        Start a private session for a channel.
        
        Args:
            channel_id: Discord channel ID
            server_id: Discord server ID
            duration_minutes: Duration in minutes
            started_by: User ID who started the session
            
        Returns:
            End time of the session
        """
        end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        self._active_sessions[channel_id] = {
            'end_time': end_time,
            'started_by': started_by,
            'server_id': server_id,
            'duration_minutes': duration_minutes
        }
        
        logger.info(f"Private session started for channel {channel_id} by user {started_by}, ends at {end_time}")
        
        # Start cleanup task if not already running
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        
        return end_time
    
    def stop_session(self, channel_id: int) -> bool:
        """
        Stop a private session for a channel.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            True if session was stopped, False if no active session
        """
        if channel_id in self._active_sessions:
            session_info = self._active_sessions.pop(channel_id)
            logger.info(f"Private session stopped for channel {channel_id} (was started by user {session_info['started_by']})")
            return True
        return False
    
    def is_channel_private(self, channel_id: int) -> bool:
        """
        Check if a channel is currently in a private session.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            True if channel is in private session
        """
        if channel_id not in self._active_sessions:
            return False
        
        # Check if session has expired
        session = self._active_sessions[channel_id]
        if datetime.utcnow() >= session['end_time']:
            # Session expired, remove it
            self._active_sessions.pop(channel_id)
            logger.info(f"Private session for channel {channel_id} expired")
            return False
        
        return True
    
    def get_session_info(self, channel_id: int) -> Optional[Dict]:
        """
        Get information about an active session.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            Session info dict or None if no active session
        """
        if not self.is_channel_private(channel_id):
            return None
        
        return self._active_sessions.get(channel_id)
    
    def get_all_active_sessions(self, server_id: Optional[int] = None) -> Dict[int, Dict]:
        """
        Get all active sessions, optionally filtered by server.
        
        Args:
            server_id: Optional server ID to filter by
            
        Returns:
            Dict of channel_id -> session_info
        """
        # Clean up expired sessions first
        self._cleanup_expired()
        
        if server_id is None:
            return self._active_sessions.copy()
        
        return {
            channel_id: info
            for channel_id, info in self._active_sessions.items()
            if info['server_id'] == server_id
        }
    
    def get_time_remaining(self, channel_id: int) -> Optional[timedelta]:
        """
        Get time remaining for a session.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            Time remaining or None if no active session
        """
        if not self.is_channel_private(channel_id):
            return None
        
        session = self._active_sessions[channel_id]
        remaining = session['end_time'] - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def _cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            channel_id
            for channel_id, session in self._active_sessions.items()
            if now >= session['end_time']
        ]
        
        for channel_id in expired:
            self._active_sessions.pop(channel_id)
            logger.info(f"Removed expired private session for channel {channel_id}")
    
    async def _cleanup_expired_sessions(self):
        """Background task to periodically clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                self._cleanup_expired()
                
                # Stop task if no active sessions
                if not self._active_sessions:
                    logger.info("No active private sessions, stopping cleanup task")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in private session cleanup task: {e}")


# Global instance
private_session_manager = PrivateSessionManager()
