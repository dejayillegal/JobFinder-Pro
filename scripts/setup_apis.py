
#!/usr/bin/env python3
"""Interactive script to set up API credentials for job connectors."""

import os
from pathlib import Path

def setup_adzuna():
    """Configure Adzuna API credentials."""
    print("\n📋 Adzuna API Setup")
    print("=" * 50)
    print("Get free credentials at: https://developer.adzuna.com/")
    print()
    
    app_id = input("Enter your Adzuna App ID (or press Enter to skip): ").strip()
    if not app_id:
        print("⏭️  Skipping Adzuna setup")
        return None
    
    app_key = input("Enter your Adzuna App Key: ").strip()
    
    return {
        "ADZUNA_APP_ID": app_id,
        "ADZUNA_APP_KEY": app_key
    }

def update_env_file(credentials):
    """Update .env file with credentials."""
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print(f"⚠️  .env file not found. Creating from .env.example")
        example_path = Path(__file__).parent.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text())
        else:
            env_path.touch()
    
    # Read current .env
    lines = env_path.read_text().splitlines()
    updated_lines = []
    keys_to_add = set(credentials.keys())
    
    # Update existing keys
    for line in lines:
        updated = False
        for key, value in credentials.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}")
                keys_to_add.discard(key)
                updated = True
                break
        if not updated:
            updated_lines.append(line)
    
    # Add new keys
    for key in keys_to_add:
        updated_lines.append(f"{key}={credentials[key]}")
    
    # Write back
    env_path.write_text("\n".join(updated_lines) + "\n")
    print(f"✅ Updated {env_path}")

def main():
    print("🚀 JobFinder Pro - API Credentials Setup")
    print("=" * 50)
    print()
    print("This script will help you configure API credentials for job connectors.")
    print()
    
    all_credentials = {}
    
    # Adzuna
    adzuna_creds = setup_adzuna()
    if adzuna_creds:
        all_credentials.update(adzuna_creds)
        all_credentials["MOCK_CONNECTORS"] = "false"
    else:
        all_credentials["MOCK_CONNECTORS"] = "true"
    
    if all_credentials:
        print("\n💾 Saving credentials to .env file...")
        update_env_file(all_credentials)
        print()
        print("✅ Setup complete!")
        print()
        print("Next steps:")
        print("1. Restart your API server workflow")
        print("2. Upload a resume to test real job matching")
        print()
        print("Job sources enabled:")
        if adzuna_creds:
            print("  ✅ Adzuna (Real API)")
        print("  ✅ Indeed (RSS Feeds)")
        print("  ⏭️  Jooble (Mock - API not yet configured)")
        print("  ⏭️  LinkedIn (Mock - ToS compliance)")
        print("  ⏭️  Naukri (Mock - robots.txt compliance)")
    else:
        print("\n⚠️  No credentials configured. Using mock data.")

if __name__ == "__main__":
    main()
