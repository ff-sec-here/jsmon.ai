#!/usr/bin/env python3

import os
import shutil
import json
import subprocess
import sys

def check_and_install_dependencies():
    """Check if dependencies are installed and offer to install them."""
    try:
        import requests
        import decouple
        import jsbeautifier
        import slack_sdk
        import google.generativeai
        print("✓ All major dependencies are installed.")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e.name}")
        answer = input("Would you like to install all required dependencies from requirements.txt? (y/n) ").lower()
        if answer == 'y':
            print("Installing dependencies...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✓ Dependencies installed successfully.")
                return True
            except subprocess.CalledProcessError:
                print("✗ Failed to install dependencies. Please install them manually using: pip install -r requirements.txt")
                return False
        else:
            print("Please install dependencies manually to continue.")
            return False

def setup_jsmon_ai():
    """Setup script for JSMon.ai features."""
    print("JSMon.ai Setup")

    # 1. Check dependencies
    if not check_and_install_dependencies():
        print("Setup aborted due to missing dependencies.")
        return

    # 2. Check for .env file
    if not os.path.exists('.env'):
        print("\nCreating a default .env file...")
        with open('.env', 'w') as f:
            f.write("# Telegram Notifications (required for alerts)\n")
            f.write("JSMON_NOTIFY_TELEGRAM=true\n")
            f.write("JSMON_TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN\n")
            f.write("JSMON_TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID\n\n")
            f.write("# Slack Notifications (optional)\n")
            f.write("JSMON_NOTIFY_SLACK=false\n")
            f.write("JSMON_SLACK_TOKEN=YOUR_SLACK_BOT_TOKEN\n")
            f.write("JSMON_SLACK_CHANNEL_ID=YOUR_SLACK_CHANNEL_ID\n\n")
            f.write("# AI Configuration (required for analysis)\n")
            f.write("GEMINI_API_KEY=YOUR_GEMINI_API_KEY\n")
            f.write("GEMINI_MODEL=gemini-2.5-pro\n")
        print("✓ Created .env file.")
        print("  IMPORTANT: Please edit the .env file with your API keys and tokens.")
    else:
        print("\n✓ .env file already exists.")

    # 3. Check directories
    print("\nChecking directory structure...")
    # These are created by the app now, but we can ensure targets exists.
    directories = ['targets']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created {directory} directory")
        else:
            print(f"✓ {directory} directory already exists")

    # 4. Check if targets directory has files
    target_files = os.listdir('targets') if os.path.exists('targets') else []
    if not target_files:
        print("\n⚠️  Warning: No target files found in 'targets' directory.")
        print("   To get started, add URLs to monitor in text files within the 'targets' directory.")
        print("   For example: echo \"https://example.com/app.js\" > targets/example.txt")

    print("\n" + "=" * 50)
    print("✅ Setup is complete!")
    print("\nNext steps:")
    print("1. If you haven't already, edit the .env file with your API keys.")
    print("2. Add URLs to monitor in the 'targets' directory.")
    print("3. Run the application: python jsmon-ai.py")
    print("\nFor a Gemini API key, visit: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    setup_jsmon_ai()
