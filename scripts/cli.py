#!/usr/bin/env python3
"""CLI utilities for JobFinder Pro administration."""

import click
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.app.core.database import SessionLocal
from api.app.core.security import get_password_hash
from api.app.models.user import User
from api.app.models.job import Job, JobMatch


@click.group()
def cli():
    """JobFinder Pro CLI utilities."""
    pass


@cli.command()
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--name', prompt=True, help='Full name')
def create_admin(email: str, password: str, name: str):
    """Create a new admin user."""
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            click.echo(f"❌ User with email {email} already exists!")
            return
        
        # Create admin user
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=name,
            is_active=True,
            is_admin=True
        )
        db.add(user)
        db.commit()
        
        click.echo(f"✅ Admin user created successfully!")
        click.echo(f"   Email: {email}")
        click.echo(f"   Name: {name}")
    
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error creating admin user: {str(e)}")
    
    finally:
        db.close()


@cli.command()
@click.option('--days', default=30, help='Remove jobs older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup_old_jobs(days: int, dry_run: bool):
    """Clean up old job listings and matches."""
    db: Session = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count jobs to delete
        old_jobs = db.query(Job).filter(Job.created_at < cutoff_date).all()
        job_count = len(old_jobs)
        
        if job_count == 0:
            click.echo(f"✅ No jobs older than {days} days found.")
            return
        
        if dry_run:
            click.echo(f"🔍 DRY RUN: Would delete {job_count} jobs older than {days} days")
            for job in old_jobs[:5]:
                click.echo(f"   - {job.title} at {job.company} (created {job.created_at})")
            if job_count > 5:
                click.echo(f"   ... and {job_count - 5} more")
        else:
            # Delete old jobs (cascades to matches)
            for job in old_jobs:
                db.delete(job)
            db.commit()
            
            click.echo(f"✅ Deleted {job_count} old jobs and their matches")
    
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error cleaning up jobs: {str(e)}")
    
    finally:
        db.close()


@cli.command()
def stats():
    """Show database statistics."""
    db: Session = SessionLocal()
    
    try:
        user_count = db.query(User).count()
        job_count = db.query(Job).count()
        match_count = db.query(JobMatch).count()
        
        click.echo("📊 Database Statistics")
        click.echo("=" * 40)
        click.echo(f"Users:       {user_count:,}")
        click.echo(f"Jobs:        {job_count:,}")
        click.echo(f"Matches:     {match_count:,}")
        click.echo("=" * 40)
        
        # Recent activity
        recent_users = db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        recent_matches = db.query(JobMatch).filter(
            JobMatch.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        click.echo("\n📈 Last 7 Days")
        click.echo("=" * 40)
        click.echo(f"New users:   {recent_users:,}")
        click.echo(f"New matches: {recent_matches:,}")
        click.echo("=" * 40)
    
    finally:
        db.close()


@cli.command()
@click.option('--email', prompt=True, help='User email')
def reset_password(email: str):
    """Reset user password."""
    db: Session = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            click.echo(f"❌ User not found: {email}")
            return
        
        new_password = click.prompt("New password", hide_input=True, confirmation_prompt=True)
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        click.echo(f"✅ Password reset for {email}")
    
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error resetting password: {str(e)}")
    
    finally:
        db.close()


if __name__ == '__main__':
    cli()
