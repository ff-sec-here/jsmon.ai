#!/usr/bin/env python3

import json
from datetime import datetime
from typing import Dict, Any, Tuple

from .gemini_client import AIProviderAPI
from .storage_manager import StorageManager

class SummaryManager:
    """Manages the generation, saving, and retrieval of AI-powered summaries."""

    def __init__(self, gemini_client: AIProviderAPI, storage_manager: StorageManager) -> None:
        self.gemini_client = gemini_client
        self.storage_manager = storage_manager
        
    def load_prompt_template(self, template_path: str) -> str:
        """Load a prompt template from a file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def generate_and_save_summary(self, js_url: str, file_hash: str, file_content: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a new summary, save it, and return the summary object and metadata."""
        template = self.load_prompt_template("AI/prompts/code-summary.md")
        if not template:
            template = "Please provide a comprehensive summary of this JavaScript code in JSON format:"
                
        json_string = self.gemini_client.generate_summary(file_content, template)
        summary_object = self._parse_json_from_ai_response(json_string)

        self.storage_manager.save_summary(file_hash, summary_object)
        
        metadata = {
            'js_url': js_url,
            'file_hash': file_hash,
            'timestamp': datetime.now().isoformat(),
            'file_size': len(file_content),
            'template_used': 'code-summary.md' if template else 'default'
        }
        
        return summary_object, metadata

    def _parse_json_from_ai_response(self, json_string: str) -> Dict[str, Any]:
        """Strip markdown fences and parse a JSON string from an AI response."""
        clean_string = json_string.strip()
        if clean_string.startswith("```json"):
            clean_string = clean_string[7:].strip()
        if clean_string.endswith("```"):
            clean_string = clean_string[:-3].strip()
        
        try:
            return json.loads(clean_string)
        except json.JSONDecodeError:
            return {
                "error": "AI response was not valid JSON after cleaning",
                "raw_response": json_string
            }
    
    def get_summary(self, file_hash: str) -> Dict[str, Any]:
        """Retrieve an existing file summary using the StorageManager."""
        return self.storage_manager.get_summary(file_hash)
