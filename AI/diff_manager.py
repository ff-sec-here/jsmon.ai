#!/usr/bin/env python3

import difflib
import jsbeautifier
from typing import List
from .storage_manager import StorageManager

class DiffManager:
    """Handles the generation of textual and HTML diffs between file versions."""

    def __init__(self, storage_manager: StorageManager) -> None:
        self.storage_manager = storage_manager
        self.beautify_options = {
            "indent_with_tabs": 1,
            "keep_function_indentation": 0,
        }

    def _get_beautified_content(self, file_hash: str) -> List[str]:
        """Retrieve and beautify the content of a stored file."""
        content = self.storage_manager.get_content(file_hash)
        if content is None:
            return []
        return jsbeautifier.beautify(content, self.beautify_options).splitlines(keepends=True)

    def get_html_diff(self, old_hash: str, new_hash: str) -> str:
        """Generate a styled HTML diff between two file versions."""
        try:
            old_lines = [line.rstrip('\r\n') for line in self._get_beautified_content(old_hash)]
            new_lines = [line.rstrip('\r\n') for line in self._get_beautified_content(new_hash)]

            differ = difflib.HtmlDiff(wrapcolumn=80)
            return differ.make_file(
                old_lines,
                new_lines,
                fromdesc=f"Previous version ({old_hash})",
                todesc=f"Current version ({new_hash})"
            )
        except Exception as e:
            return f"<html><body><h1>Error generating diff</h1><p>{str(e)}</p></body></html>"

    def get_text_diff(self, old_hash: str, new_hash: str) -> str:
        """Get a plain text unified diff for AI analysis."""
        try:
            old_lines = self._get_beautified_content(old_hash)
            new_lines = self._get_beautified_content(new_hash)
            
            diff_lines = list(difflib.unified_diff(
                old_lines, 
                new_lines, 
                fromfile=f"previous/{old_hash}", 
                tofile=f"current/{new_hash}",
                lineterm=""
            ))
            
            return "\n".join(diff_lines)
        except Exception as e:
            return f"Error generating diff: {str(e)}"