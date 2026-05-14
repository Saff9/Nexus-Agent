#!/usr/bin/env python3
"""Cron scheduler for automated agent tasks."""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Job:
    """Represents a scheduled job."""
    id: str
    name: str
    schedule: str  # Cron format or special: @daily, @hourly, etc.
    prompt: str
    created_at: str
    next_run: str
    last_run: Optional[str] = None
    enabled: bool = True
    skills: List[str] = None
    output_target: Optional[str] = None  # Where to send results
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        return cls(**data)


class CronScheduler:
    """Scheduler for automated agent tasks."""
    
    SPECIAL_SCHEDULES = {
        "@hourly": 3600,
        "@daily": 86400,
        "@weekly": 604800,
        "@monthly": 2592000,
        "@yearly": 31536000,
    }
    
    def __init__(self, data_dir: Path, agent_factory: Callable, delivery_callback: Callable = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_file = self.data_dir / "cron_jobs.json"
        
        self.agent_factory = agent_factory
        self.delivery_callback = delivery_callback  # For sending results
        
        self.jobs: Dict[str, Job] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        self._load_jobs()
    
    def _load_jobs(self):
        """Load jobs from file."""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    data = json.load(f)
                    for job_data in data:
                        job = Job.from_dict(job_data)
                        self.jobs[job.id] = job
                logger.info(f"Loaded {len(self.jobs)} cron jobs")
            except Exception as e:
                logger.error(f"Error loading jobs: {e}")
    
    def _save_jobs(self):
        """Save jobs to file."""
        try:
            with open(self.jobs_file, 'w') as f:
                json.dump([job.to_dict() for job in self.jobs.values()], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
    
    def _parse_schedule(self, schedule: str) -> Optional[int]:
        """Parse schedule string to seconds until next run."""
        if schedule in self.SPECIAL_SCHEDULES:
            return self.SPECIAL_SCHEDULES[schedule]
        
        # Simple cron parsing (minute, hour, day, month, weekday)
        # This is simplified - full cron parsing would be more complex
        try:
            parts = schedule.split()
            if len(parts) == 5:
                minute, hour, day, month, weekday = parts
                # Calculate next run (simplified)
                now = datetime.now()
                next_run = now.replace(minute=int(minute), hour=int(hour), second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return (next_run - now).total_seconds()
        except Exception as e:
            logger.error(f"Cron parse error: {e}")
        
        return None
    
    def add_job(self, name: str, schedule: str, prompt: str, 
                skills: List[str] = None, output_target: str = None) -> Job:
        """Add a new scheduled job."""
        job_id = f"job_{len(self.jobs) + 1}_{int(time.time())}"
        now = datetime.utcnow().isoformat()
        
        # Calculate first run
        seconds = self._parse_schedule(schedule)
        if seconds is None:
            seconds = 3600  # Default to 1 hour
        
        next_run = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
        
        job = Job(
            id=job_id,
            name=name,
            schedule=schedule,
            prompt=prompt,
            created_at=now,
            next_run=next_run,
            skills=skills or [],
            output_target=output_target
        )
        
        self.jobs[job_id] = job
        self._save_jobs()
        
        logger.info(f"Added cron job: {name} ({schedule})")
        return job
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a job."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_jobs()
            logger.info(f"Removed job: {job_id}")
            return True
        return False
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs."""
        return [job.to_dict() for job in self.jobs.values()]
    
    def enable_job(self, job_id: str) -> bool:
        """Enable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            self._save_jobs()
            return True
        return False
    
    def disable_job(self, job_id: str) -> bool:
        """Disable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
            self._save_jobs()
            return True
        return False
    
    def _run_job(self, job: Job):
        """Execute a job."""
        logger.info(f"Running cron job: {job.name}")
        
        try:
            # Create agent with job-specific skills
            agent = self.agent_factory()
            
            # Attach skills if specified
            for skill_name in job.skills:
                if skill_name in agent.skills:
                    agent.skills[skill_name]['enabled'] = True
            
            # Run the job
            response = agent.run_conversation(job.prompt)
            
            # Deliver results
            if self.delivery_callback:
                self.delivery_callback(job.output_target, response)
            
            # Update job
            job.last_run = datetime.utcnow().isoformat()
            seconds = self._parse_schedule(job.schedule)
            if seconds:
                job.next_run = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
            
            self._save_jobs()
            logger.info(f"Job completed: {job.name}")
            
        except Exception as e:
            logger.error(f"Job failed: {job.name} - {e}")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("Cron scheduler started")
        
        while not self._stop_event.is_set():
            now = datetime.utcnow()
            
            for job in list(self.jobs.values()):
                if not job.enabled:
                    continue
                
                next_run = datetime.fromisoformat(job.next_run)
                if now >= next_run:
                    # Run job in thread
                    thread = threading.Thread(target=self._run_job, args=(job,))
                    thread.start()
            
            # Check every 30 seconds
            self._stop_event.wait(30)
        
        logger.info("Cron scheduler stopped")
    
    def start(self):
        """Start the scheduler."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()
        logger.info("✓ Cron scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Cron scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            "running": self._running,
            "job_count": len(self.jobs),
            "enabled_jobs": sum(1 for j in self.jobs.values() if j.enabled),
            "jobs": self.list_jobs()
        }
