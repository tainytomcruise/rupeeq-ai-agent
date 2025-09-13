# RupeeQ AI Calling Agent Project

## Project Overview
This project implements an AI-based calling assistant and real-time dashboard for RupeeQ, a financial backup company that provides loans through digital telecom and telecalling.

## Project Components

### 1. AI-Based Calling Assistant
- **Speech Recognition & Synthesis**: Real-time audio processing using Python
- **Conversation Engine**: Rule-based dialogue management with finite state machine
- **Script Integration**: Implements the provided RupeeQ calling script
- **Real-time Demo**: Interactive voice/text interface for demonstration

### 2. Real-Time Dashboard
- **Live Monitoring**: Real-time call tracking and auto-refresh
- **Performance Analytics**: Call metrics, sentiment analysis, and insights
- **Data Management**: Export functionality and comprehensive reporting

## Technology Stack
- **Backend**: Python (Flask)
- **Speech Processing**: SpeechRecognition, pyttsx3, vosk
- **NLP**: spaCy, transformers
- **Frontend**: HTML, CSS, JavaScript (Chart.js)
- **Database**: SQLite (for demo purposes)
- **Real-time**: WebSocket for live updates

## Installation & Setup

### Local Development

#### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd rupeeq-ai-agent

# Run setup script
chmod +x setup.sh
./setup.sh

# Start the application
source venv/bin/activate
python3 run.py
```

#### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python3 run.py
```

### Access the Application
- **Dashboard**: http://localhost:8080
- **AI Agent Interface**: http://localhost:8080/ai-agent

## 🚀 Deployment

### GitHub & Vercel Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/rupeeq-ai-agent.git
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import your GitHub repository
   - Vercel will auto-deploy using `vercel.json`

3. **Access your live demo**
   - Your Vercel URL will be provided after deployment
   - Dashboard: `https://your-project.vercel.app/`
   - AI Agent: `https://your-project.vercel.app/ai-agent`

📚 **For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

## Project Structure
```
rupeeq-ai-project/
├── app.py                 # Main Flask application
├── ai_agent/             # AI calling assistant modules
│   ├── speech_engine.py  # Speech recognition & synthesis
│   ├── conversation.py    # Dialogue management
│   └── script_handler.py # RupeeQ script implementation
├── dashboard/            # Dashboard components
│   ├── static/          # CSS, JS, images
│   └── templates/       # HTML templates
├── database/            # Database models and migrations
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Features

### AI Calling Assistant
- Real-time speech recognition and synthesis
- Script-based conversation flow
- Customer information collection
- Eligibility checking simulation
- Multi-language support (Hindi/English)

### Real-Time Dashboard
- Live call monitoring
- Performance metrics and analytics
- Call transcript management
- Export and reporting capabilities
- Responsive design for mobile/desktop

## Implementation Approach

### Phase 1: Core AI Agent
1. Speech recognition using vosk for real-time processing
2. Text-to-speech using pyttsx3 for voice responses
3. Finite state machine for conversation flow
4. Integration with RupeeQ calling script

### Phase 2: Dashboard Development
1. Real-time data visualization
2. Performance metrics calculation
3. Export and reporting functionality
4. Responsive UI design

### Phase 3: Integration & Testing
1. End-to-end testing
2. Performance optimization
3. Documentation and deployment

## Usage Examples

### Starting a Call
```python
from ai_agent.conversation import ConversationManager

# Initialize conversation
conversation = ConversationManager()
conversation.start_call("Customer Name")
```

### Dashboard Access
- Open browser and navigate to `http://localhost:5000`
- View real-time call statistics
- Analyze performance metrics
- Export call data and reports

## Contributing
This project is designed as a demonstration of AI calling agent capabilities. For production use, additional security, scalability, and compliance measures should be implemented.

## License
This project is created for RupeeQ evaluation purposes.


