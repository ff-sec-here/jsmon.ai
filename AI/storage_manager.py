#!/usr/bin/env python3

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class StorageManager:
    """Manages all file system interactions for storing and retrieving monitored data."""

    def __init__(self, monitored_dir: str = "monitored_files", tracking_file: str = "jsmon.ai.json") -> None:
        self.monitored_dir = Path(monitored_dir)
        self.tracking_file = Path(tracking_file)

    def get_hash(self, content: str) -> str:
        """Generate a 10-character MD5 hash for a string."""
        return hashlib.md5(content.encode("utf8")).hexdigest()[:10]

    def get_storage_path(self, file_hash: str) -> Path:
        """Get the storage path for a specific file hash, creating it if necessary."""
        path = self.monitored_dir / file_hash
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_content_path(self, file_hash: str) -> Path:
        """Get the path for storing a file's content."""
        return self.get_storage_path(file_hash) / "content.js"

    def get_metadata_path(self, file_hash: str) -> Path:
        """Get the path for storing a file's metadata."""
        return self.get_storage_path(file_hash) / "metadata.json"

    def get_summary_path(self, file_hash: str) -> Path:
        """Get the path for storing a file's AI summary."""
        return self.get_storage_path(file_hash) / "summary.json"

    def save_content(self, file_hash: str, file_content: str) -> Path:
        """Save file content to its hash-based directory."""
        content_path = self.get_content_path(file_hash)
        with open(content_path, "w", encoding='utf-8') as f:
            f.write(file_content)
        return content_path

    def save_metadata(self, file_hash: str, metadata: Dict[str, Any]) -> Path:
        """Save file metadata to its hash-based directory."""
        metadata_path = self.get_metadata_path(file_hash)
        with open(metadata_path, "w", encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return metadata_path

    def save_summary(self, file_hash: str, summary_object: Dict[str, Any]) -> Path:
        """Save a summary object to its hash-based directory as a JSON file."""
        summary_path = self.get_summary_path(file_hash)
        with open(summary_path, "w", encoding='utf-8') as f:
            json.dump(summary_object, f, indent=2, ensure_ascii=False)
        return summary_path

    def get_content(self, file_hash: str) -> Optional[str]:
        """Retrieve file content from its hash-based directory."""
        content_path = self.get_content_path(file_hash)
        if content_path.exists():
            with open(content_path, "r", encoding='utf-8') as f:
                return f.read()
        return None

    def get_summary(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a summary object from its hash-based directory."""
        summary_path = self.get_summary_path(file_hash)
        if summary_path.exists():
            try:
                with open(summary_path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                return None
        return None

    def get_tracking_data(self) -> Dict[str, List[str]]:
        """Load and return the entire tracking data from the JSON file."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, "r", encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_tracking_data(self, data: Dict[str, List[str]]) -> None:
        """Save the provided data to the tracking JSON file."""
        with open(self.tracking_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_hash_history(self, js_url: str) -> List[str]:
        """Get the list of historical hashes for a given URL."""
        tracking_data = self.get_tracking_data()
        return tracking_data.get(js_url, [])

    def get_initial_hash(self, js_url: str) -> Optional[str]:
        """Get the first hash recorded for a URL."""
        history = self.get_hash_history(js_url)
        return history[0] if history else None

    def get_previous_hash(self, js_url: str) -> Optional[str]:
        """Get the most recent hash recorded for a URL."""
        history = self.get_hash_history(js_url)
        return history[-1] if history else None

    def update_tracking_file(self, js_url: str, file_hash: str) -> None:
        """Add a new hash to the history for a given URL."""
        tracking_data = self.get_tracking_data()
        history = tracking_data.get(js_url, [])
        if file_hash not in history:
            history.append(file_hash)
        tracking_data[js_url] = history
        self.save_tracking_data(tracking_data)

    def get_file_stats(self, file_hash: str) -> Optional[os.stat_result]:
        """Get file statistics for a monitored file."""
        content_path = self.get_content_path(file_hash)
        if content_path.exists():
            return content_path.stat()
        return None