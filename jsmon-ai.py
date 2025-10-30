#!/usr/bin/env python3

import requests
import re
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from decouple import config

# Import AI components
from AI.gemini_client import AIProviderAPI
from AI.storage_manager import StorageManager
from AI.summary_manager import SummaryManager
from AI.change_analyzer import ChangeAnalyzer
from AI.diff_manager import DiffManager
from AI.notification_manager import NotificationManager

# --- Configuration ---
TARGETS_DIR = "targets"
LOGS_DIR = "logs"
AI_LOGS_DIR = "logs/ai_conversations"
AUTO_GENERATE_SUMMARIES = config("AUTO_GENERATE_SUMMARIES", default=True, cast=bool)
MAX_DIFF_SIZE = config("MAX_DIFF_SIZE", default=50000, cast=int)
LOG_AI_RESPONSES = config("LOG_AI_RESPONSES", default=True, cast=bool)

# --- Pre-flight Directory Setup ---
# Ensure all necessary directories exist before any other code runs.
Path(LOGS_DIR).mkdir(exist_ok=True)
Path(AI_LOGS_DIR).mkdir(parents=True, exist_ok=True)
Path(TARGETS_DIR).mkdir(exist_ok=True)


# Setup logging configuration
logger = logging.getLogger('JSMon.ai')
logger.setLevel(logging.INFO)
logger.propagate = False

# Create different formatters for file and console
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(message)s')

# Configure file handler
file_handler = logging.FileHandler('logs/jsmon.log')
file_handler.setFormatter(file_formatter)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Add handlers only if they haven't been added before
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# --- Configuration ---
TARGETS_DIR = "targets"
LOGS_DIR = "logs"
AI_LOGS_DIR = "logs/ai_conversations"
AUTO_GENERATE_SUMMARIES = config("AUTO_GENERATE_SUMMARIES", default=True, cast=bool)
MAX_DIFF_SIZE = config("MAX_DIFF_SIZE", default=50000, cast=int)
LOG_AI_RESPONSES = config("LOG_AI_RESPONSES", default=True, cast=bool)

# --- Component Initialization ---
try:
    gemini_client = AIProviderAPI()
    storage_manager = StorageManager()
    diff_manager = DiffManager(storage_manager)
    summary_manager = SummaryManager(gemini_client, storage_manager)
    change_analyzer = ChangeAnalyzer(gemini_client)
    notification_manager = NotificationManager()
except Exception as e:
    logger.critical(f"A critical component failed to initialize: {e}", exc_info=True)
    storage_manager = None

# --- Helper Functions ---
def log_ai_response(response_type: str, js_url: str, file_hash: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Log AI responses to files for debugging and auditing."""
    if not LOG_AI_RESPONSES:
        return
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "response_type": response_type,
            "js_url": js_url,
            "file_hash": file_hash,
            "content": content,
            "metadata": metadata or {}
        }
        log_filename = Path(AI_LOGS_DIR) / f"{response_type}_{file_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to log AI response: {str(e)}")

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid-looking URL."""
    regex = re.compile(r'^https?://.*', re.IGNORECASE)
    return re.match(regex, url) is not None

def get_js_file_list(target_dir: str) -> List[str]:
    """Load JavaScript file URLs from the target directory."""
    js_files: List[str] = []
    target_path = Path(target_dir)
    if not target_path.exists():
        logger.warning(f"Target directory {target_dir} does not exist")
        return []
    for file_path in target_path.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and is_valid_url(line.strip())]
                    js_files.extend(urls)
            except Exception as e:
                logger.error(f"Failed to read target file {file_path}: {str(e)}")
    return js_files

def get_js_file(js_url: str) -> str:
    """Fetch JavaScript file from a URL and return its content."""
    try:
        r = requests.get(js_url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch {js_url}: {str(e)}")



# --- Notification Orchestration ---
def notify_change(js_url: str, prev_hash: str, new_hash: str) -> None:
    """Orchestrate the notification process for a detected change."""
    if not all([change_analyzer, notification_manager, diff_manager, summary_manager]):
        logger.warning("A required manager is not initialized. Skipping change notification.")
        return

    logger.info(f"Analyzing changes for {js_url} from {prev_hash} to {new_hash}")
    try:
        initial_hash = storage_manager.get_initial_hash(js_url)
        summary_obj = summary_manager.get_summary(initial_hash) if initial_hash else None
        summary_for_prompt = json.dumps(summary_obj, indent=2) if summary_obj else "No initial summary available."

        diff_text = diff_manager.get_text_diff(prev_hash, new_hash)
        if len(diff_text) > MAX_DIFF_SIZE:
            diff_text = diff_text[:MAX_DIFF_SIZE] + "\n... [truncated]"

        analysis_obj = change_analyzer.analyze_code_changes(summary_for_prompt, diff_text, js_url)
        
        risk_level = analysis_obj.get("risk_level", "UNKNOWN")
        short_summary = analysis_obj.get("short_summary", "Analysis could not be summarized.")
        detailed_analysis = analysis_obj.get("detailed_analysis", {})
        full_analysis_str = json.dumps(analysis_obj, indent=2)

        diff_html = diff_manager.get_html_diff(prev_hash, new_hash)
        summary_html = _generate_summary_html(detailed_analysis)

        notification_manager.send_analysis_notification(js_url, full_analysis_str, risk_level, diff_html, summary_html, short_summary)

        log_ai_response("change_analysis", js_url, new_hash, analysis_obj, {"risk_level": risk_level})

    except Exception as e:
        logger.error(f"Failed during change analysis/notification for {js_url}: {e}", exc_info=True)

def notify_new_file(js_url: str, file_hash: str) -> None:
    """Orchestrate the notification for a newly enrolled file."""
    if not all([notification_manager, summary_manager]):
        logger.warning("A required manager is not initialized. Skipping new file notification.")
        return

    logger.info(f"Sending notification for new file: {js_url}")
    try:
        summary_obj = summary_manager.get_summary(file_hash)
        summary_text = "Summary was not generated for this new file."

        if summary_obj:
            if 'error' in summary_obj:
                summary_text = f"Could not generate summary: {summary_obj['error']}"
            elif 'concise_summary' in summary_obj:
                summary_text = summary_obj['concise_summary']
            else:
                summary_text = "Summary was generated but could not be parsed."
        
        notification_manager.send_new_file_notification(js_url, summary_text)
    except Exception as e:
        logger.error(f"Failed to send new file notification for {js_url}: {e}", exc_info=True)

# --- Main Application Logic ---
def main() -> None:
    """Main entry point for the JSMon.ai application."""
    logger.info("=" * 60)
    logger.info("JSMon.ai - JavaScript File Monitor with AI Analysis")
    logger.info("=" * 60)

    if not storage_manager:
        logger.critical("StorageManager failed to initialize. Application cannot continue.")
        sys.exit(1)

    
    js_files = get_js_file_list(TARGETS_DIR)
    if not js_files:
        logger.error(f"No valid JavaScript URLs found in {TARGETS_DIR} directory.")
        sys.exit(1)
        
    logger.info(f"Monitoring {len(js_files)} JavaScript files...")

    for js_url in js_files:
        logger.info(f"\nChecking: {js_url}")
        try:
            js_content = get_js_file(js_url)
            current_hash = storage_manager.get_hash(js_content)

            prev_hash = storage_manager.get_previous_hash(js_url)
            if current_hash == prev_hash:
                logger.info(f"  ✓ No changes detected")
                continue

            is_new_file = prev_hash is None

            storage_manager.save_content(current_hash, js_content)
            storage_manager.update_tracking_file(js_url, current_hash)
            
            metadata = {
                "js_url": js_url,
                "file_hash": current_hash,
                "timestamp": datetime.now().isoformat(),
                "file_size": len(js_content),
            }
            storage_manager.save_metadata(current_hash, metadata)

            if is_new_file:
                logger.info(f"  ✓ New JavaScript file enrolled: {js_url}")
                if summary_manager and AUTO_GENERATE_SUMMARIES:
                    summary_obj, ai_meta = summary_manager.generate_and_save_summary(js_url, current_hash, js_content)
                    log_ai_response("summary", js_url, current_hash, summary_obj, ai_meta)
                notify_new_file(js_url, current_hash)
            else:
                logger.warning(f"  ! Changes detected: {js_url}")
                notify_change(js_url, prev_hash, current_hash)
                            
        except Exception as e:
            logger.error(f"  ✗ Error processing JavaScript file {js_url}: {e}", exc_info=True)
            continue
    
    logger.info("=" * 60)
    logger.info("JSMon scan completed successfully")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
