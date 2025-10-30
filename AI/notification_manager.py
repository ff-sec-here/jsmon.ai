#!/usr/bin/env python3

import requests
import logging
from typing import Dict, Any, Optional
from decouple import config

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    logging.warning("Slack SDK not installed. Slack notifications will be disabled.")
    WebClient = None
    SlackApiError = None

logger = logging.getLogger(__name__)

class NotificationManager:
    """Handles sending notifications to configured channels like Telegram and Slack."""

    def __init__(self) -> None:
        self.telegram_token = config("JSMON_TELEGRAM_TOKEN", default="CHANGEME")
        self.telegram_chat_id = config("JSMON_TELEGRAM_CHAT_ID", default="CHANGEME")
        self.slack_token = config("JSMON_SLACK_TOKEN", default="CHANGEME")
        self.slack_channel_id = config("JSMON_SLACK_CHANNEL_ID", default="CHANGEME")
        self.notify_slack = config("JSMON_NOTIFY_SLACK", default=False, cast=bool)
        self.notify_telegram = config("JSMON_NOTIFY_TELEGRAM", default=False, cast=bool)
        
        self.slack_client: Optional[WebClient] = None
        if self.notify_slack and self.slack_token != "CHANGEME" and WebClient:
            self.slack_client = WebClient(token=self.slack_token)
        elif self.notify_slack:
            logger.warning("Slack notifications enabled but Slack SDK or token is not configured.")
            self.notify_slack = False

    def send_analysis_notification(self, js_url: str, analysis: str, risk_level: str, diff_html: str, summary_html: str, short_summary: str) -> Dict[str, Any]:
        """Send change analysis notification via configured channels."""
        results = {}
        if self.notify_telegram:
            results['telegram'] = self._send_telegram_analysis(js_url, risk_level, short_summary, diff_html, summary_html)
        if self.notify_slack and self.slack_client:
            results['slack'] = self._send_slack_analysis(js_url, risk_level, short_summary, diff_html, summary_html)
        return results

    def send_new_file_notification(self, js_url: str, summary: str) -> Dict[str, Any]:
        """Send new file notification via configured channels."""
        results = {}
        if self.notify_telegram:
            results['telegram'] = self._send_new_file_telegram(js_url, summary)
        if self.notify_slack and self.slack_client:
            results['slack'] = self._send_new_file_slack(js_url, summary)
        return results

    def _send_telegram_analysis(self, js_url: str, risk_level: str, short_summary: str, diff_html: str, summary_html: str) -> Optional[requests.Response]:
        """Send change analysis results via Telegram."""
        risk_emoji = {"HIGH": "🚨", "MEDIUM": "⚠️", "LOW": "ℹ️"}
        emoji = risk_emoji.get(risk_level, "ℹ️")
        
        message = f"{emoji} <b>JavaScript Change Analysis</b>\n\n"
        message += f"<b>File URL:</b> {js_url}\n\n"
        message += f"<b>Risk Level:</b> {risk_level}\n\n"
        message += short_summary
        
        try:
            response = self._send_telegram_message(message)
            if response and response.ok:
                self._send_telegram_document(js_url, diff_html, "diff.html", "Diff file")
                self._send_telegram_document(js_url, summary_html, "summary.html", "Summary of changes")
            return response
        except Exception as e:
            logger.error(f"Error sending Telegram analysis notification: {e}", exc_info=True)
            return None

    def _send_new_file_telegram(self, js_url: str, summary: str) -> Optional[requests.Response]:
        """Send new file notification via Telegram."""
        message = f"✅ <b>New JavaScript File Enrolled</b>\n\n"
        message += f"<b>File URL:</b> {js_url}\n\n"
        message += f"<b>Summary:</b>\n{summary[:3000]}..."
        return self._send_telegram_message(message)

    def _send_telegram_message(self, message: str) -> Optional[requests.Response]:
        if self.telegram_token == "CHANGEME": return None
        payload = {'chat_id': self.telegram_chat_id, 'text': message, 'parse_mode': 'HTML'}
        try:
            return requests.post(f"https://api.telegram.org/bot{self.telegram_token}/sendMessage", data=payload)
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}", exc_info=True)
            return None

    def _send_telegram_document(self, js_url: str, content: str, filename: str, caption_prefix: str) -> None:
        payload = {'chat_id': self.telegram_chat_id, 'caption': f'{caption_prefix} for {js_url}'}
        files = {'document': (filename, content)}
        try:
            requests.post(f"https://api.telegram.org/bot{self.telegram_token}/sendDocument", files=files, data=payload)
        except Exception as e:
            logger.error(f"Error sending Telegram document {filename}: {e}", exc_info=True)

    def _send_slack_analysis(self, js_url: str, risk_level: str, short_summary: str, diff_html: str, summary_html: str) -> Optional[Dict[str, Any]]:
        """Send change analysis results via Slack."""
        if not self.slack_client or not SlackApiError:
            return None
        
        risk_emoji = {"HIGH": "🚨", "MEDIUM": "⚠️", "LOW": "ℹ️"}
        emoji = risk_emoji.get(risk_level, "ℹ️")
        
        message = f"{emoji} *JavaScript Change Analysis*\n\n"
        message += f"*File URL:* {js_url}\n\n"
        message += f"*Risk Level:* {risk_level}\n\n"
        message += short_summary
        
        try:
            response = self.slack_client.chat_postMessage(channel=self.slack_channel_id, text=message, mrkdwn=True)
            if response.get('ok'):
                self._send_slack_file(js_url, diff_html, "diff.html", "Diff for")
                self._send_slack_file(js_url, summary_html, "summary.html", "Summary for")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending Slack analysis notification: {e.response['error']}")
            return None

    def _send_new_file_slack(self, js_url: str, summary: str) -> Optional[Dict[str, Any]]:
        """Send new file notification via Slack."""
        if not self.slack_client or not SlackApiError:
            return None

        message = f"✅ *New JavaScript File Enrolled*\n\n"
        message += f"*File URL:* {js_url}\n\n"
        message += f"*Summary:*\n```{{summary}}```"
        try:
            return self.slack_client.chat_postMessage(channel=self.slack_channel_id, text=message, mrkdwn=True)
        except SlackApiError as e:
            logger.error(f"Error sending new file Slack notification: {e.response['error']}")
            return None

    def _send_slack_file(self, js_url: str, content: str, filename: str, title_prefix: str) -> None:
        try:
            self.slack_client.files_upload(
                channels=self.slack_channel_id,
                content=content,
                filename=filename,
                filetype="html",
                title=f"{title_prefix} {js_url}",
                initial_comment=f"{title_prefix} changes in {js_url}"
            )
        except SlackApiError as e:
            logger.error(f"Error uploading Slack file {filename}: {e.response['error']}")
