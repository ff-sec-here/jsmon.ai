#!/usr/bin/env python3

import json
import os
from typing import Dict, Any

from .gemini_client import AIProviderAPI

class ChangeAnalyzer:
    """Handles the AI-powered analysis of code changes."""

    def __init__(self, gemini_client: AIProviderAPI) -> None:
        self.gemini_client = gemini_client
        
    def load_prompt_template(self, template_path: str) -> str:
        """Load a prompt template from a file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def analyze_code_changes(self, file_summary: str, diff_content: str, js_url: str) -> Dict[str, Any]:
        """Analyze code changes and return a structured dictionary."""
        template = self.load_prompt_template("AI/prompts/code-analysis.md")
                
        formatted_template = template.format(
            file_summary=file_summary,
            diff_content=diff_content,
            js_url=js_url
        )
        
        json_string = self.gemini_client.generate_response(formatted_template, config_name="code_analysis")
        return self._parse_json_from_ai_response(json_string)

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
                "raw_response": json_string,
                "short_summary": "Could not analyze changes due to an AI response error.",
                "risk_level": "UNKNOWN"
            }
