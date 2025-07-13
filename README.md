# 🤖 Sanya AI - Your Systematic Artificial Neural Yielded Assistant

A sophisticated Jarvis-like AI assistant built with Python, featuring voice interaction, natural language processing, and comprehensive system automation capabilities.

## 🌟 Features

### 🎤 Voice Interface
- **Custom Wake Word Detection**: Uses "Sanya" as the wake word with custom ONNX model
- **Speech Recognition**: Google Speech Recognition for accurate voice input
- **Text-to-Speech**: Coqui TTS with Jenny voice model for natural responses
- **Mood-Aware Responses**: Adjusts tone based on user sentiment analysis

### 🧠 AI & Memory
- **Google Gemini 2.0 Flash**: Advanced language model for intelligent responses
- **Memory Management**: 
  - Short-term memory for conversation context
  - Long-term memory with vector storage for persistent knowledge
  - Automatic memory snapshots and cleanup
- **Sentiment Analysis**: Real-time mood detection using DistilBERT

### 💻 System Control
- **File Operations**: Create, edit, read, delete, copy, and search files
- **System Monitoring**: CPU usage, memory status, process listing
- **Command Execution**: Run system commands with timeout protection
- **App Launcher**: Open applications by voice command

### 🔧 Code Development
- **Python Script Execution**: Run and test Python scripts
- **Web Development**: Create and serve web applications
- **Code Project Management**: Multi-step project creation with testing
- **Automated Testing**: Built-in test case execution and validation

### 🌐 Web Integration
- **Web Search**: DuckDuckGo integration for real-time information
- **Email Notifications**: SMTP-based notification system
- **Task Scheduling**: Automated task execution with configurable intervals

### 📊 Logging & Monitoring
- **Comprehensive Logging**: All activities logged to `logs/sanya.log`
- **Performance Tracking**: Command execution time monitoring
- **Error Handling**: Robust error handling with detailed logging

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary support)
- Microphone and speakers
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sanya_ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password_here
   ```

4. **Run the assistant**
   ```bash
   python main.py
   ```

## 🎯 Usage Examples

### Voice Commands

#### System Control
- "Sanya, check CPU usage"
- "Sanya, what's the current time?"
- "Sanya, open Chrome"
- "Sanya, execute command dir"

#### File Operations
- "Sanya, create a file called notes.txt"
- "Sanya, read the file config.json"
- "Sanya, edit the file script.py"
- "Sanya, search for files with .py extension"

#### Code Development
- "Sanya, write a Python script to calculate factorial"
- "Sanya, create a web app for a todo list"
- "Sanya, run the test script"
- "Sanya, edit the main function"

#### Information & Search
- "Sanya, search for Python tutorials"
- "Sanya, what's the weather like?"
- "Sanya, tell me about machine learning"

### Exit Commands
- "Goodbye"
- "Exit"
- "Thank you"
- "Your work is done"

## 🏗️ Project Structure

```
sanya_ai/
├── core/                          # Core AI functionality
│   ├── assistant.py              # Main assistant loop
│   ├── llm.py                    # Language model integration
│   ├── memory_manager.py         # Memory management system
│   └── task_manager.py           # Task routing and execution
├── modules/                       # Feature modules
│   ├── voice_interface.py        # Speech recognition & TTS
│   ├── wakeword_detector.py      # Custom wake word detection
│   ├── system_control.py         # System operations
│   ├── file_control.py           # File management
│   ├── code_executor.py          # Code execution & testing
│   ├── app_launcher.py           # Application launcher
│   ├── mood_manager.py           # Sentiment analysis
│   └── vector_store.py           # Vector database operations
├── custom_wake_word/             # Custom wake word models
│   └── sanya/
│       ├── sanya.onnx           # ONNX wake word model
│       └── sanya.tflite         # TensorFlow Lite model
├── memory/                       # Memory storage
│   ├── short_term.json          # Short-term memory
│   └── long_term/               # Long-term memory snapshots
├── logs/                         # Application logs
├── sanya-tts/                    # TTS model files
├── main.py                       # Application entry point
└── requirements.txt              # Python dependencies
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key for AI responses
- `EMAIL_ADDRESS`: Gmail address for notifications
- `EMAIL_PASSWORD`: Gmail app password for SMTP

### Customization
- **Wake Word**: Replace `custom_wake_word/sanya/` models with your own
- **Voice Model**: Modify TTS model in `voice_interface.py`
- **Memory Settings**: Adjust memory thresholds in `memory_manager.py`
- **Logging**: Configure log levels and paths in individual modules

## 🛠️ Development

### Adding New Features
1. Create a new module in the `modules/` directory
2. Add task routing in `core/task_manager.py`
3. Update the LLM prompt in `core/llm.py`
4. Add voice command examples to this README

### Testing
- Run individual modules for unit testing
- Use the built-in test framework for code projects
- Check logs in `logs/sanya.log` for debugging

## 📝 Logging

All activities are logged to `logs/sanya.log` with timestamps and context:
- Voice interactions
- System commands
- File operations
- AI responses
- Error messages
- Performance metrics

## 🔒 Security Considerations

- API keys are stored in environment variables
- System commands have timeout protection
- File operations are restricted to project directory
- Email notifications use secure SMTP

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini**: Advanced language model
- **Coqui TTS**: Text-to-speech synthesis
- **OpenWakeWord**: Wake word detection framework
- **DuckDuckGo**: Web search integration
- **Transformers**: Sentiment analysis models

## 🆘 Troubleshooting

### Common Issues

1. **Wake word not detected**
   - Check microphone permissions
   - Verify audio device settings
   - Ensure wake word models are in correct location

2. **Speech recognition errors**
   - Check internet connection
   - Verify microphone is working
   - Try speaking more clearly

3. **TTS not working**
   - Check speaker connections
   - Verify TTS model files are present
   - Check audio device settings

4. **API errors**
   - Verify API keys in `.env` file
   - Check API quota limits
   - Ensure internet connectivity

### Getting Help
- Check the logs in `logs/sanya.log`
- Review error messages in console output
- Verify all dependencies are installed
- Ensure environment variables are set correctly

---

**Sanya AI** - Your intelligent companion for productivity and automation! 🤖✨ 