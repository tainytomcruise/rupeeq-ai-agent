#!/usr/bin/env python3
"""
RupeeQ AI Calling Agent Launcher
"""
import os
from app import app, socketio

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Print startup message
    print("🚀 Starting RupeeQ AI Calling Agent...")
    print("📊 Dashboard: http://localhost:8080")
    print("🤖 AI Agent: http://localhost:8080/ai-agent")
    print("Press Ctrl+C to stop the server")
    
    # Run the application
    socketio.run(app, 
                 host='0.0.0.0',
                 port=8080,
                 debug=True,
                 use_reloader=True)
