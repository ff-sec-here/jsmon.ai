#!/usr/bin/env python3

import google.generativeai as genai
import logging
from decouple import config

logger = logging.getLogger(__name__)

import json
from typing import Dict, Any

class AIProviderAPI:
    """A client to interact with the Google Gemini API, configured via config.json."""

    def __init__(self) -> None:
        self.api_key = config("GEMINI_API_KEY", default="CHANGEME")
        if self.api_key == "CHANGEME":
            raise ValueError("GEMINI_API_KEY not configured. Please set it in your .env file.")
        
        genai.configure(api_key=self.api_key)
        self.configs = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Loads the AI model configurations from config.json."""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse config.json: {e}. Using default fallback configs.")
            return {
                "summarization": {"model": "gemini-1.5-flash", "max_tokens": 4096, "temperature": 0.5},
                "code_analysis": {"model": "gemini-1.5-flash", "max_tokens": 8192, "temperature": 0.7}
            }

    def generate_response(self, prompt: str, config_name: str) -> str:
        """Generate a response from the Gemini API for a given prompt and config."""
        try:
            task_config = self.configs.get(config_name)
            if not task_config:
                raise ValueError(f"Configuration '{config_name}' not found in config.json")

            model = genai.GenerativeModel(task_config['model'])
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=task_config['max_tokens'],
                    temperature=task_config['temperature'],
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            return f'{{"error": "Failed to generate AI response: {str(e)}"}}'
    
    def generate_summary(self, code_content: str, prompt_template: str) -> str:
        """Generate a code summary by prepending the code to the prompt template."""
        full_prompt = f"{prompt_template}\n\n{code_content}"
        return self.generate_response(full_prompt, config_name="summarization")
    
    def analyze_changes(self, file_summary: str, diff_content: str, prompt_template: str) -> str:
        """Analyze code changes. This method is kept for compatibility but is less used now."""
        # The full context is now formatted in the prompt template itself.
        return self.generate_response(prompt_template)
