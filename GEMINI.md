# JSMon - JavaScript File Monitor with AI Analysis

**Version:** 1.0.0  
**AI Provider:** Google Gemini  
**Language:** Python 3  

## Overview

JSMon is an advanced JavaScript file monitoring tool that combines traditional file change detection with powerful AI-driven analysis capabilities. It monitors JavaScript files from specified URLs, detects changes, and provides intelligent insights using Google's Gemini AI model.

## 🚀 Core Features

### 1. File Monitoring & Change Detection
- **URL-based monitoring**: Monitor JavaScript files from any accessible URL
- **Hash-based change detection**: Efficient detection using MD5 hashing
- **File versioning**: Maintains history of all file versions
- **Automatic enrollment**: New files are automatically added to monitoring

### 2. AI-Powered Analysis
- **Code summarization**: Comprehensive analysis of JavaScript files
- **Change analysis**: Detailed assessment of code modifications
- **Risk assessment**: Automatic risk level classification (HIGH/MEDIUM/LOW)
- **Security impact analysis**: Identification of potential security implications

### 3. Smart Notifications
- **Telegram integration**: Send analysis results and alerts via Telegram
- **Slack integration**: Post notifications to Slack channels
- **Risk-based alerts**: Different notification styles based on risk level
- **File attachments**: Send diff files for detailed review

### 4. Comprehensive Logging
- **AI response logging**: All AI interactions are logged for audit
- **Daily aggregated logs**: JSONL format for easy processing
- **Metadata tracking**: File sizes, timestamps, and analysis metadata

## 📋 Current Functions

### Core Functions

#### `main()`
- **Purpose**: Main entry point of the application
- **Functionality**: Orchestrates the entire monitoring process
- **Features**:
  - Configuration validation
  - Directory initialization
  - File monitoring loop
  - Error handling and reporting

#### `get_js_file_list(targetdir)`
- **Purpose**: Load JavaScript file URLs from target directory
- **Input**: Directory path containing URL files
- **Output**: List of JavaScript URLs to monitor
- **Features**: Filters hidden files and handles multiple URL files

#### `get_js_file(js_url)`
- **Purpose**: Fetch JavaScript content from URL
- **Input**: JavaScript file URL
- **Output**: File content as string
- **Features**: 
  - URL validation
  - HTTP error handling
  - 30-second timeout
  - Request exception handling

#### `get_hash(string)`
- **Purpose**: Generate MD5 hash for content comparison
- **Input**: File content string
- **Output**: 10-character hash string
- **Use**: Efficient change detection

#### `save_js_file(js_url, file_hash, file_content, is_new_file=False)`
- **Purpose**: Save file content and update tracking data
- **Features**:
  - JSON metadata management
  - File versioning
  - Automatic AI summarization for new files
  - UTF-8 encoding support

#### `get_previous_file_hash(js_url)`
- **Purpose**: Retrieve the last known hash for a URL
- **Output**: Previous hash or None for new files
- **Use**: Change detection comparison

#### `notify(js_url, prev, new)`
- **Purpose**: Handle change notifications and AI analysis
- **Features**:
  - AI-powered change analysis
  - Risk level assessment
  - Multi-channel notifications
  - Diff generation and attachment

### Utility Functions

#### `is_valid_url(url)`
- **Purpose**: Validate URL format
- **Features**: Regex-based validation for HTTP/HTTPS/FTP URLs

#### `get_diff(old, new)` / `get_diff_text(old, new)`
- **Purpose**: Generate visual and text diffs
- **Features**: JavaScript code beautification and comparison

#### `log_ai_response(response_type, js_url, file_hash, content, metadata=None)`
- **Purpose**: Log AI interactions for audit and debugging
- **Features**: JSON logging with timestamps and metadata

### AI Components

#### `AIProviderAPI` (Gemini Client)
- **Purpose**: Interface with Google Gemini API
- **Features**:
  - Configurable model and parameters
  - Template-based prompting
  - Error handling and logging
  - Context-aware generation

#### `SummaryManager`
- **Purpose**: Generate and manage file summaries
- **Features**:
  - Template-based analysis
  - Summary persistence
  - Metadata tracking
  - Duplicate prevention

#### `ChangeAnalyzer`
- **Purpose**: Analyze code changes and assess risk
- **Features**:
  - Diff analysis
  - Risk level extraction
  - Change categorization
  - Template-based evaluation

#### `NotificationManager`
- **Purpose**: Handle multi-channel notifications
- **Features**:
  - Telegram bot integration
  - Slack webhook support
  - Risk-based formatting
  - File attachment support

## 🔧 Configuration

### Environment Variables

#### Core Configuration
- `AUTO_GENERATE_SUMMARIES`: Auto-generate summaries for new files (default: true)
- `MAX_DIFF_SIZE`: Maximum diff size for analysis (default: 50000)
- `LOG_AI_RESPONSES`: Enable AI response logging (default: true)

#### Gemini API Configuration
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `GEMINI_MODEL`: Model to use (default: gemini-1.5-flash)
- `GEMINI_MAX_TOKENS`: Maximum response tokens (default: 8192)
- `GEMINI_TEMPERATURE`: Response creativity (default: 0.7)

#### Notification Configuration
- `JSMON_TELEGRAM_TOKEN` / `TELEGRAM_TOKEN`: Telegram bot token
- `JSMON_TELEGRAM_CHAT_ID` / `TELEGRAM_CHAT_ID`: Telegram chat ID
- `JSMON_SLACK_TOKEN` / `SLACK_TOKEN`: Slack bot token
- `JSMON_SLACK_CHANNEL_ID` / `SLACK_CHANNEL_ID`: Slack channel ID
- `JSMON_NOTIFY_TELEGRAM` / `NOTIFY_TELEGRAM`: Enable Telegram notifications
- `JSMON_NOTIFY_SLACK` / `NOTIFY_SLACK`: Enable Slack notifications

## 📁 Directory Structure

```
jsmon.ai/
├── jsmon-ai.py                    # Main application
├── AI/                         # AI components package
│   ├── __init__.py            # Package initialization
│   ├── gemini_client.py       # Gemini API client
│   ├── summary_manager.py     # File summarization
│   ├── change_analyzer.py     # Change analysis
│   └── notification_manager.py # Notification handling
├── prompts/                   # AI prompt templates
│   ├── code-summary.md       # File summary template
│   └── code-analysis.md      # Change analysis template
├── targets/                  # URL files for monitoring
├── downloads/                # Downloaded JS files and metadata
├── logs/                    # AI response logs
│   └── ai_responses/        # Daily AI interaction logs
└── jsmon.json              # File tracking metadata
```

## 🔄 Workflow

1. **Initialization**
   - Load configuration
   - Initialize AI components
   - Create required directories
   - Validate settings

2. **File Discovery**
   - Read URL files from `targets/` directory
   - Validate URLs
   - Prepare monitoring list

3. **Monitoring Loop**
   - Fetch each JavaScript file
   - Calculate content hash
   - Compare with previous version
   - Process changes if detected

4. **Change Processing**
   - Save new file version
   - Generate AI summary (for new files)
   - Analyze changes (for modifications)
   - Send notifications
   - Log all AI interactions

5. **AI Analysis**
   - Retrieve previous file summary
   - Generate change analysis
   - Assess risk level
   - Format for notifications

6. **Notification Delivery**
   - Format messages by risk level
   - Send via configured channels
   - Attach diff files
   - Log delivery results

## 🛡️ Security Features

- **Input validation**: URL and content validation
- **Error isolation**: Failures don't stop monitoring
- **Secure logging**: Sensitive data handling
- **API key protection**: Environment-based configuration
- **File integrity**: Hash-based verification

## 🚨 Risk Assessment

The AI system automatically classifies changes into three risk levels:

- **HIGH**: Critical security issues, major functional changes
- **MEDIUM**: Moderate changes with potential impact
- **LOW**: Minor changes, cosmetic updates

## 📊 Monitoring & Observability

- **Real-time status**: Console output with timestamps
- **AI interaction logs**: Complete audit trail
- **File version history**: All changes tracked
- **Notification delivery logs**: Success/failure tracking
- **Error reporting**: Comprehensive error handling

## 🔗 Integration Points

- **Google Gemini API**: AI analysis and summarization
- **Telegram Bot API**: Instant notifications
- **Slack API**: Team collaboration
- **File system**: Local storage and caching
- **HTTP/HTTPS**: Remote file fetching

## 📈 Performance Considerations

- **Diff size limiting**: Large diffs are truncated
- **Concurrent processing**: Single-threaded by design
- **Memory management**: File streaming and cleanup
- **Rate limiting**: Respectful API usage
- **Caching**: Summary and metadata persistence

## 🔧 Troubleshooting

### Common Issues

1. **AI Import Errors**: Ensure `AI/__init__.py` exists
2. **Gemini API Errors**: Verify API key and quota
3. **Notification Failures**: Check tokens and permissions
4. **File Access Issues**: Verify URL accessibility
5. **Permission Errors**: Check file system permissions

### Debug Features

- Comprehensive error logging
- AI response logging
- Step-by-step console output
- File operation validation
- Network error handling

## 🚀 Future Enhancements

- Multi-threaded processing
- Database integration
- Web dashboard
- Custom alert rules
- Machine learning improvements
- Advanced diff algorithms

---

**Last Updated:** October 2024  
**AI Model:** Google Gemini 1.5 Flash  
**Status:** Production Ready