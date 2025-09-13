# RupeeQ AI Calling Agent - Implementation Guide

## Project Overview

This project implements a complete AI-based calling assistant and real-time dashboard for RupeeQ, a financial company offering overdraft facilities. The system includes:

1. **AI-Based Calling Assistant** - Automated conversation handling based on RupeeQ's calling script
2. **Real-Time Dashboard** - Performance monitoring and analytics
3. **Speech Processing** - Voice input/output capabilities
4. **Database Management** - Call tracking and transcript storage

## Key Features Implemented

### ✅ AI Calling Assistant
- **Script-based Conversation Flow**: Implements the complete RupeeQ overdraft calling script
- **State Machine Management**: Handles conversation states (greeting, information collection, objection handling, etc.)
- **Multi-language Support**: English and Hindi language support
- **Objection Handling**: Predefined responses for common customer objections
- **Real-time Speech Processing**: Voice input recognition and text-to-speech output

### ✅ Real-Time Dashboard
- **Live Monitoring**: Real-time call tracking and statistics
- **Performance Metrics**: Connection rates, call duration, sentiment analysis
- **Call Management**: View call details, transcripts, and outcomes
- **Filtering & Search**: Advanced filtering by date, status, duration, keywords
- **Export Functionality**: CSV export of call data and reports
- **Responsive Design**: Works on desktop and mobile devices

### ✅ Speech Engine
- **Speech Recognition**: Real-time voice input using Google Speech Recognition
- **Text-to-Speech**: High-quality voice output using pyttsx3
- **Language Support**: Indian English and Hindi support
- **Error Handling**: Robust error handling and fallback mechanisms

### ✅ Database System
- **SQLite Database**: Lightweight, file-based database
- **Call Tracking**: Complete call lifecycle management
- **Transcript Storage**: Message-by-message conversation storage
- **Performance Metrics**: Daily statistics and analytics
- **Data Export**: CSV export capabilities

## Technical Architecture

### Backend (Python Flask)
- **Flask**: Web framework for API endpoints
- **Flask-SocketIO**: Real-time WebSocket communication
- **SQLite**: Database for data persistence
- **SpeechRecognition**: Voice input processing
- **pyttsx3**: Text-to-speech synthesis

### Frontend (HTML/CSS/JavaScript)
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Data visualization
- **Socket.IO Client**: Real-time communication
- **Web Speech API**: Browser-based speech recognition

### Database Schema
```
calls:
- id, customer_name, agent_name, phone_number
- status, outcome, sentiment_score
- start_time, end_time, duration, language
- customer_data (JSON), created_at

transcripts:
- id, call_id, speaker, message
- timestamp, sentiment, intent

performance_metrics:
- id, date, total_calls, connected_calls
- not_connected, busy, failed
- interested, not_interested, call_back
- avg_duration, avg_sentiment
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Microphone and speakers for voice features

### Quick Start
```bash
# Clone or download the project
cd "RupeeQ project"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
# OR use the startup script
./start.sh
```

### Manual Setup
```bash
# Install core dependencies
pip install Flask==2.3.3 Flask-SocketIO==5.3.6
pip install SpeechRecognition==3.10.0 pyttsx3==2.90
pip install eventlet==0.33.3

# For audio processing (optional)
pip install pyaudio  # May require system audio libraries
```

## Usage Guide

### 1. Starting the Application
```bash
python run.py
```
- Dashboard: http://localhost:8080
- AI Agent Interface: http://localhost:8080/ai-agent

### 2. AI Agent Interface
1. **Set Customer Details**: Enter customer name and agent name
2. **Choose Language**: Select English (India) or Hindi
3. **Start Call**: Click "Start Call" to begin conversation
4. **Voice Input**: Click "Start Listening" for voice input
5. **Text Input**: Type responses in the text field
6. **End Call**: Click "End Call" to finish

### 3. Dashboard Features
- **Live Statistics**: View real-time call metrics
- **Call History**: Browse past calls with details
- **Filtering**: Filter calls by date, status, outcome
- **Export**: Download call data as CSV
- **Transcripts**: View complete conversation transcripts

## Conversation Flow

The AI agent follows the RupeeQ script structure:

1. **Greeting**: Welcome customer and introduce agent
2. **Script Introduction**: Explain overdraft facility
3. **Recording Notice**: Inform about call recording
4. **Employment Status**: Check if customer is employed
5. **Salary Collection**: Gather salary information
6. **Benefits Explanation**: Explain overdraft benefits
7. **Personal Details**: Collect customer information
8. **Eligibility Check**: Process eligibility verification
9. **Bureau Consent**: Get consent for credit check
10. **Document Requirements**: List required documents
11. **Call Closing**: End call with next steps

### Objection Handling
The system handles common objections:
- "I don't need a loan"
- "I already have a loan"
- "What's the interest rate?"
- "I need time to think"
- "Can I withdraw cash?"
- "No EMI burden"
- "Why are you recording?"
- "I have a credit card"

## API Endpoints

### Dashboard APIs
- `GET /api/calls` - Get call statistics and recent calls
- `GET /api/calls/<id>` - Get specific call details
- `POST /api/calls/filtered` - Get filtered calls
- `POST /api/calls/export` - Export calls to CSV

### WebSocket Events
- `start_call` - Begin new call session
- `end_call` - End current call
- `user_message` - Process user input
- `start_listening` - Begin voice input
- `stop_listening` - Stop voice input

## Configuration

### Speech Engine Settings
```python
# In ai_agent/speech_engine.py
self.recognizer.energy_threshold = 4000
self.recognizer.pause_threshold = 0.8
self.tts_engine.setProperty('rate', 150)  # Words per minute
self.tts_engine.setProperty('volume', 0.9)
```

### Database Configuration
```python
# In database/models.py
db_path = 'rupeeq_ai.db'  # SQLite database file
```

## Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Check microphone permissions
   - Ensure internet connection (uses Google Speech API)
   - Try different browsers (Chrome recommended)

2. **Text-to-Speech Not Working**
   - Check system audio output
   - Install required TTS voices
   - Verify pyttsx3 installation

3. **Database Errors**
   - Check file permissions for rupeeq_ai.db
   - Ensure SQLite is properly installed
   - Verify database schema initialization

4. **WebSocket Connection Issues**
   - Check firewall settings
   - Verify port 8080 is available
   - Try different browsers

### Performance Optimization

1. **Database Performance**
   - Regular cleanup of old data
   - Proper indexing on frequently queried columns
   - Connection pooling for high traffic

2. **Speech Processing**
   - Adjust energy threshold for noisy environments
   - Use shorter phrase time limits for faster response
   - Implement audio preprocessing for better accuracy

## Security Considerations

1. **Data Privacy**
   - Customer data is stored locally in SQLite
   - No external data transmission except speech recognition
   - Implement data retention policies

2. **Access Control**
   - Add authentication for production use
   - Implement role-based access control
   - Secure WebSocket connections

3. **Data Encryption**
   - Encrypt sensitive customer data
   - Secure database file permissions
   - Use HTTPS in production

## Future Enhancements

### Planned Features
1. **Advanced NLP**: Integration with OpenAI GPT or similar
2. **Sentiment Analysis**: Real-time emotion detection
3. **Call Recording**: Audio file storage and playback
4. **Multi-agent Support**: Multiple concurrent agents
5. **CRM Integration**: Connect with existing customer systems
6. **Analytics Dashboard**: Advanced reporting and insights

### Technical Improvements
1. **Microservices Architecture**: Break into smaller services
2. **Container Deployment**: Docker containerization
3. **Cloud Integration**: AWS/Azure deployment
4. **Real-time Analytics**: Stream processing for live metrics
5. **Machine Learning**: Predictive analytics and optimization

## Support & Maintenance

### Regular Maintenance
- Update dependencies monthly
- Monitor database size and performance
- Review and clean old call data
- Test speech recognition accuracy
- Backup database regularly

### Monitoring
- Application logs in console output
- Database performance metrics
- Speech recognition success rates
- WebSocket connection stability

## Conclusion

This implementation provides a complete, functional AI calling agent system that meets the requirements specified in the RupeeQ project brief. The system is designed to be:

- **Scalable**: Can handle multiple concurrent calls
- **Maintainable**: Clean code structure and documentation
- **Extensible**: Easy to add new features and integrations
- **User-friendly**: Intuitive interfaces for both agents and administrators

The system successfully addresses the main issues mentioned:
- ✅ Text-to-speech functionality working
- ✅ Voice input recognition implemented
- ✅ Start/End call buttons functional
- ✅ Conversation flow continues properly
- ✅ Complete dashboard with real-time monitoring
- ✅ Database integration for call tracking
- ✅ Export and reporting capabilities

For questions or support, refer to the code documentation or contact the development team.

