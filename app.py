#!/usr/bin/env python3
"""
RupeeQ AI Calling Agent - Main Flask Application
"""

import os
import sqlite3
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import csv
import io
from typing import Dict, List, Optional, Any

# Import our modules
from ai_agent.speech_engine import SpeechEngine
from ai_agent.conversation import ConversationManager
from database.models import DatabaseManager, Call, Transcript, PerformanceMetrics

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rupeeq_ai_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for active sessions
active_calls = {}
speech_engines = {}
conversation_managers = {}

# Initialize database manager
db_manager = DatabaseManager()

# Flask Routes
@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/ai-agent')
def ai_agent():
    """AI Agent interface route"""
    return render_template('ai_agent.html')

# API Routes for Dashboard
@app.route('/api/calls', methods=['GET'])
def get_calls():
    """Get all calls with statistics"""
    try:
        # Get daily statistics
        stats = db_manager.get_daily_statistics()
        
        # Get active calls count
        active_calls_count = len(active_calls)
        
        # Get recent calls
        recent_calls_data = db_manager.get_calls(limit=10)
        recent_calls = []
        for call in recent_calls_data:
            recent_calls.append({
                'id': call.id,
                'customer_name': call.customer_name,
                'status': call.status,
                'duration': call.duration or 0,
                'start_time': call.start_time,
                'outcome': call.outcome or 'Unknown',
                'sentiment_score': call.sentiment_score or 0
            })
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_calls_today': stats['total_calls'],
                'active_calls': active_calls_count,
                'connection_rate': stats['connection_rate'],
                'avg_call_duration': stats['avg_duration']
            },
            'status_counts': {
                'completed': stats['connected_calls'],
                'in_progress': active_calls_count,
                'not_connected': stats['not_connected'],
                'busy': stats['busy'],
                'failed': stats['failed']
            },
            'outcome_distribution': stats['outcome_counts'],
            'recent_calls': recent_calls
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls/<int:call_id>', methods=['GET'])
def get_call_details(call_id):
    """Get detailed information about a specific call"""
    try:
        # Get call details
        call = db_manager.get_call(call_id)
        if not call:
            return jsonify({'success': False, 'error': 'Call not found'}), 404
        
        # Get transcripts
        transcripts_data = db_manager.get_transcripts(call_id)
        transcripts = []
        for transcript in transcripts_data:
            transcripts.append({
                'speaker': transcript.speaker,
                'message': transcript.message,
                'timestamp': transcript.timestamp,
                'timestamp_formatted': datetime.fromisoformat(transcript.timestamp).strftime('%H:%M:%S') if transcript.timestamp else ''
            })
        
        call_info = {
            'id': call.id,
            'customer_name': call.customer_name,
            'agent_name': call.agent_name,
            'phone_number': call.phone_number,
            'status': call.status,
            'outcome': call.outcome,
            'sentiment_score': call.sentiment_score,
            'start_time': call.start_time,
            'end_time': call.end_time,
            'duration': call.duration,
            'language': call.language,
            'duration_formatted': f"{call.duration//60}:{call.duration%60:02d}" if call.duration else "0:00"
        }
        
        return jsonify({
            'success': True,
            'call': call_info,
            'transcripts': transcripts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls/filtered', methods=['POST'])
def get_filtered_calls():
    """Get filtered calls based on criteria"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        # Get filtered calls using database manager
        calls_data = db_manager.get_calls(filters=filters, limit=filters.get('limit', 100))
        
        calls = []
        for call in calls_data:
            calls.append({
                'id': call.id,
                'customer_name': call.customer_name,
                'status': call.status,
                'duration': call.duration or 0,
                'start_time': call.start_time,
                'outcome': call.outcome or 'Unknown',
                'sentiment_score': call.sentiment_score or 0,
                'duration_formatted': f"{call.duration//60}:{call.duration%60:02d}" if call.duration else "0:00"
            })
        
        return jsonify({
            'success': True,
            'calls': calls,
            'count': len(calls)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls/export', methods=['POST'])
def export_calls():
    """Export filtered calls to CSV"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        conn = sqlite3.connect('rupeeq_ai.db')
        cursor = conn.cursor()
        
        # Build query with filters (similar to filtered calls)
        query = '''
            SELECT * FROM calls WHERE 1=1
        '''
        params = []
        
        if filters.get('start_date'):
            query += ' AND DATE(start_time) >= ?'
            params.append(filters['start_date'])
            
        if filters.get('end_date'):
            query += ' AND DATE(start_time) <= ?'
            params.append(filters['end_date'])
            
        if filters.get('status'):
            query += ' AND status = ?'
            params.append(filters['status'])
            
        if filters.get('outcome'):
            query += ' AND outcome = ?'
            params.append(filters['outcome'])
        
        query += ' ORDER BY start_time DESC'
        
        cursor.execute(query, params)
        calls = cursor.fetchall()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Customer Name', 'Agent Name', 'Phone Number', 'Status', 
                        'Outcome', 'Sentiment Score', 'Start Time', 'End Time', 'Duration', 'Language'])
        
        # Write data
        for call in calls:
            writer.writerow(call)
        
        output.seek(0)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'rupeeq_calls_export_{timestamp}.csv'
        
        return jsonify({
            'success': True,
            'data': output.getvalue(),
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# SocketIO Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to RupeeQ AI Agent'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    
    # Clean up resources for this session
    if request.sid in active_calls:
        end_call_internal(request.sid)
    
    if request.sid in speech_engines:
        speech_engines[request.sid].cleanup()
        del speech_engines[request.sid]
    
    if request.sid in conversation_managers:
        del conversation_managers[request.sid]

@socketio.on('start_call')
def handle_start_call(data):
    """Handle start call request"""
    try:
        session_id = request.sid
        customer_name = data.get('customer_name', 'Unknown Customer')
        agent_name = data.get('agent_name', 'RupeeQ AI')
        language = data.get('language', 'en-IN')
        text_mode = data.get('text_mode', False)
        
        print(f"Starting call for {customer_name} with agent {agent_name}")
        
        # Initialize speech engine
        speech_engine = SpeechEngine()
        speech_engines[session_id] = speech_engine
        
        # Initialize conversation manager
        conversation_manager = ConversationManager()
        conversation_managers[session_id] = conversation_manager
        
        # Create call record in database
        call = Call(
            customer_name=customer_name,
            agent_name=agent_name,
            status='in_progress',
            start_time=datetime.now().isoformat(),
            language=language
        )
        call_id = db_manager.create_call(call)
        
        # Store call info
        active_calls[session_id] = {
            'call_id': call_id,
            'customer_name': customer_name,
            'agent_name': agent_name,
            'language': language,
            'text_mode': text_mode,
            'start_time': datetime.now(),
            'status': 'in_progress'
        }
        
        # Start conversation
        conversation_manager.start_call(customer_name, agent_name, language)
        
        # Send initial greeting - start with greeting state
        greeting = conversation_manager.get_next_message()
        if greeting:
            emit('agent_message', {
                'message': greeting,
                'state': conversation_manager.current_state.value
            })
            
            # Speak the greeting (always try to speak, regardless of text mode)
            threading.Thread(
                target=speech_engine.speak,
                args=(greeting,),
                daemon=True
            ).start()
        
        # Update call status
        emit('call_status', {'active': True})
        
        print(f"Call started successfully for {customer_name}")
        
    except Exception as e:
        print(f"Error starting call: {e}")
        emit('error', {'message': f'Failed to start call: {str(e)}'})

@socketio.on('end_call')
def handle_end_call(data=None):
    """Handle end call request"""
    end_call_internal(request.sid)

def end_call_internal(session_id):
    """Internal function to end a call"""
    try:
        if session_id not in active_calls:
            return
        
        call_info = active_calls[session_id]
        call_id = call_info['call_id']
        
        # Calculate duration
        duration = int((datetime.now() - call_info['start_time']).total_seconds())
        
        # Update database
        updates = {
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'duration': duration
        }
        db_manager.update_call(call_id, updates)
        
        # Clean up resources
        if session_id in speech_engines:
            speech_engines[session_id].cleanup()
            del speech_engines[session_id]
        
        if session_id in conversation_managers:
            del conversation_managers[session_id]
        
        del active_calls[session_id]
        
        # Notify client
        socketio.emit('call_status', {'active': False}, room=session_id)
        socketio.emit('agent_message', {
            'message': 'Call ended. Thank you for your time!',
            'state': 'ended'
        }, room=session_id)
        
        print(f"Call ended for session {session_id}")
        
    except Exception as e:
        print(f"Error ending call: {e}")

@socketio.on('user_message')
def handle_user_message(data):
    """Handle user message input"""
    try:
        session_id = request.sid
        message = data.get('message', '').strip()
        
        if not message or session_id not in active_calls:
            return
        
        # Save transcript to database
        call_info = active_calls[session_id]
        call_id = call_info['call_id']
        
        transcript = Transcript(
            call_id=call_id,
            speaker='customer',
            message=message,
            timestamp=datetime.now().isoformat()
        )
        db_manager.add_transcript(transcript)
        
        # Process message through conversation manager
        if session_id in conversation_managers:
            conversation_manager = conversation_managers[session_id]
            response = conversation_manager.process_user_input(message)
            
            if response:
                # Save agent response to database
                agent_transcript = Transcript(
                    call_id=call_id,
                    speaker='agent',
                    message=response['message'],
                    timestamp=datetime.now().isoformat()
                )
                db_manager.add_transcript(agent_transcript)
                
                # Send response to client
                emit('agent_message', {
                    'message': response['message'],
                    'state': response.get('state', 'conversation')
                })
                
                # Speak response if not in text mode
                call_info = active_calls[session_id]
                if not call_info.get('text_mode', False) and session_id in speech_engines:
                    threading.Thread(
                        target=speech_engines[session_id].speak,
                        args=(response['message'],),
                        daemon=True
                    ).start()
                elif call_info.get('text_mode', False):
                    # Even in text mode, try to speak the message
                    if session_id in speech_engines:
                        threading.Thread(
                            target=speech_engines[session_id].speak,
                            args=(response['message'],),
                            daemon=True
                        ).start()
        
    except Exception as e:
        print(f"Error processing user message: {e}")
        emit('error', {'message': f'Failed to process message: {str(e)}'})

@socketio.on('start_listening')
def handle_start_listening():
    """Handle start listening request"""
    try:
        session_id = request.sid
        
        if session_id not in speech_engines or session_id not in active_calls:
            emit('error', {'message': 'Speech engine not available'})
            return
        
        speech_engine = speech_engines[session_id]
        call_info = active_calls[session_id]
        
        def speech_callback(text):
            if text:
                # Process the recognized speech as a user message
                socketio.emit('user_message', {'message': text}, room=session_id)
        
        # Start listening
        speech_engine.start_listening(
            callback=speech_callback,
            language=call_info['language'],
            continuous=False
        )
        
        emit('listening_status', {'listening': True})
        print(f"Started listening for session {session_id}")
        
    except Exception as e:
        print(f"Error starting speech recognition: {e}")
        emit('error', {'message': f'Failed to start listening: {str(e)}'})

@socketio.on('stop_listening')
def handle_stop_listening():
    """Handle stop listening request"""
    try:
        session_id = request.sid
        
        if session_id in speech_engines:
            speech_engines[session_id].stop_listening()
            emit('listening_status', {'listening': False})
            print(f"Stopped listening for session {session_id}")
        
    except Exception as e:
        print(f"Error stopping speech recognition: {e}")
        emit('error', {'message': f'Failed to stop listening: {str(e)}'})

if __name__ == '__main__':
    # This file is imported by run.py, so this won't run directly
    print("RupeeQ AI Calling Agent app module loaded")
