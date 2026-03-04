"""
Background job scheduler for periodic tasks.
Handles hourly summarization and other maintenance tasks.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable
from config import Config

logger = logging.getLogger(__name__)


class BackgroundJobScheduler:
    """Scheduler for running periodic background tasks."""
    
    def __init__(self):
        self.jobs = []
        self.running = False
        
    def add_job(self, name: str, interval_hours: int, task: Callable):
        """
        Add a periodic job to the scheduler.
        
        Args:
            name: Job name for logging
            interval_hours: How often to run (in hours)
            task: Async function to execute
        """
        self.jobs.append({
            'name': name,
            'interval_hours': interval_hours,
            'task': task,
            'last_run': None
        })
        logger.info(f"Added background job: {name} (every {interval_hours}h)")
    
    async def run(self):
        """Start the job scheduler."""
        self.running = True
        logger.info(f"Background job scheduler started with {len(self.jobs)} jobs")
        
        while self.running:
            try:
                now = datetime.utcnow()
                
                for job in self.jobs:
                    # Check if job needs to run
                    if job['last_run'] is None:
                        # First run - execute immediately
                        should_run = True
                    else:
                        hours_since_last_run = (now - job['last_run']).total_seconds() / 3600
                        should_run = hours_since_last_run >= job['interval_hours']
                    
                    if should_run:
                        logger.info(f"Running background job: {job['name']}")
                        try:
                            await job['task']()
                            job['last_run'] = now
                            logger.info(f"Completed background job: {job['name']}")
                        except Exception as e:
                            logger.error(f"Error in background job {job['name']}: {e}", exc_info=True)
                
                # Sleep for 10 minutes before checking again
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error in background job scheduler: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop the job scheduler."""
        self.running = False
        logger.info("Background job scheduler stopped")


# Global scheduler instance
scheduler = BackgroundJobScheduler()


async def setup_background_jobs():
    """Setup all background jobs."""
    from ingestion.summarizer import run_hourly_summarization
    from utils.cleanup import cleanup_old_messages
    
    # Add hourly summarization job
    scheduler.add_job(
        name="hourly_summarization",
        interval_hours=1,
        task=lambda: run_hourly_summarization(hours_ago=1)
    )
    
    # Add cleanup job
    scheduler.add_job(
        name="message_cleanup",
        interval_hours=Config.CLEANUP_INTERVAL_HOURS,
        task=cleanup_old_messages
    )
    
    logger.info("Background jobs configured")


async def start_background_jobs():
    """Start the background job scheduler."""
    await setup_background_jobs()
    await scheduler.run()
