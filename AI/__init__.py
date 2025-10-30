#!/usr/bin/env python3

"""
AI package for JSMon - JavaScript File Monitoring Tool

This package provides AI-powered analysis capabilities including:
- File summarization using Gemini API
- Change analysis and risk assessment
- Smart notifications via Telegram and Slack
"""

__version__ = "1.0.0"
__author__ = "JSMon AI Team"

from .gemini_client import AIProviderAPI
from .summary_manager import SummaryManager
from .change_analyzer import ChangeAnalyzer
from .notification_manager import NotificationManager

__all__ = ['AIProviderAPI', 'SummaryManager', 'ChangeAnalyzer', 'NotificationManager']