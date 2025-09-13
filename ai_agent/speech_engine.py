import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import subprocess
import platform
from typing import Optional, Callable, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechEngine:
    """Speech recognition and synthesis engine for AI calling agent"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback_function = None
        self.language = 'en-IN'  # Default to Indian English
        self.listen_thread = None
        
        # Initialize TTS engine
        self._init_tts()
        
        # Configure recognizer
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 10
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            # Try pyttsx3 first
            self.tts_engine = pyttsx3.init()
            
            if self.tts_engine:
                logger.info("TTS engine initialized successfully")
                
                # Configure TTS properties
                try:
                    voices = self.tts_engine.getProperty('voices')
                    if voices:
                        # Try to find a Hindi/Indian voice
                        for voice in voices:
                            if 'hindi' in voice.name.lower() or 'indian' in voice.name.lower():
                                self.tts_engine.setProperty('voice', voice.id)
                                break
                        
                        # If no Hindi voice found, use the first available
                        if not self.tts_engine.getProperty('voice'):
                            self.tts_engine.setProperty('voice', voices[0].id)
                    
                    # Set speech rate and volume
                    self.tts_engine.setProperty('rate', 150)  # Words per minute
                    self.tts_engine.setProperty('volume', 0.9)  # Volume level
                    
                    logger.info("TTS engine configured successfully")
                except Exception as e:
                    logger.warning(f"Error configuring TTS properties: {e}")
                    # Continue with default settings
            else:
                logger.warning("TTS engine could not be initialized")
                
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self.tts_engine = None
    
    def set_language(self, language: str):
        """Set language for speech recognition and synthesis"""
        self.language = language
        logger.info(f"Language set to: {language}")
    
    def speak(self, text: str, block: bool = True):
        """Convert text to speech"""
        if not self.tts_engine:
            logger.warning("TTS engine not available")
            # Try to reinitialize
            self._init_tts()
            if not self.tts_engine:
                # Try system TTS as fallback
                return self._speak_system_tts(text, block)
        
        try:
            if block:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # Run in separate thread for non-blocking speech
                threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            # Try to reinitialize and retry once
            try:
                self._init_tts()
                if self.tts_engine:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    return True
            except:
                pass
            # Fallback to system TTS
            return self._speak_system_tts(text, block)
    
    def _speak_system_tts(self, text: str, block: bool = True):
        """Fallback TTS using system commands"""
        try:
            if platform.system() == 'Darwin':  # macOS
                # Use macOS say command
                cmd = ['say', text]
                if block:
                    subprocess.run(cmd, check=True)
                else:
                    threading.Thread(target=subprocess.run, args=(cmd,), daemon=True).start()
                logger.info("Using macOS system TTS")
                return True
            elif platform.system() == 'Linux':
                # Use espeak or festival
                try:
                    cmd = ['espeak', text]
                    if block:
                        subprocess.run(cmd, check=True)
                    else:
                        threading.Thread(target=subprocess.run, args=(cmd,), daemon=True).start()
                    logger.info("Using espeak TTS")
                    return True
                except FileNotFoundError:
                    logger.warning("espeak not found")
                    return False
            elif platform.system() == 'Windows':
                # Use Windows SAPI
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    if block:
                        speaker.Speak(text)
                    else:
                        threading.Thread(target=speaker.Speak, args=(text,), daemon=True).start()
                    logger.info("Using Windows SAPI TTS")
                    return True
                except ImportError:
                    logger.warning("pywin32 not available")
                    return False
            else:
                logger.warning("System TTS not supported on this platform")
                return False
        except Exception as e:
            logger.error(f"Error in system TTS: {e}")
            return False
    
    def _speak_thread(self, text: str):
        """Thread function for non-blocking speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in speech thread: {e}")
    
    def start_listening(self, callback: Callable[[str], None], 
                       language: str = 'en-IN', continuous: bool = False):
        """Start listening for speech input"""
        if self.is_listening:
            logger.warning("Already listening")
            return False
        
        self.callback_function = callback
        self.language = language
        self.is_listening = True
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self._listen_thread, 
                                             args=(continuous,), daemon=True)
        self.listen_thread.start()
        logger.info(f"Started listening (continuous={continuous})")
        return True
    
    def _listen_thread(self, continuous: bool):
        """Background thread for listening to audio input"""
        try:
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.is_listening:
                    try:
                        logger.info("Listening for speech...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        # Process audio in separate thread to avoid blocking
                        threading.Thread(target=self._process_audio, 
                                        args=(audio,), daemon=True).start()
                        
                        if not continuous:
                            self.is_listening = False
                            break
                            
                    except sr.WaitTimeoutError:
                        logger.info("No speech detected, continuing to listen...")
                        continue
                    except Exception as e:
                        logger.error(f"Error while listening: {e}")
                        if not continuous:
                            break
                        
        except Exception as e:
            logger.error(f"Error in listening thread: {e}")
        finally:
            self.is_listening = False
    
    def _process_audio(self, audio):
        """Process audio data and convert to text"""
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized: {text}")
            
            # Call the callback function with the recognized text
            if self.callback_function and callable(self.callback_function):
                self.callback_function(text)
                
        except sr.UnknownValueError:
            logger.info("Speech Recognition could not understand audio")
            if self.callback_function and callable(self.callback_function):
                self.callback_function("")
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    def stop_listening(self):
        """Stop listening for speech input"""
        if not self.is_listening:
            logger.warning("Not currently listening")
            return False
        
        self.is_listening = False
        
        # Wait for listen thread to finish
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        
        logger.info("Stopped listening")
        return True
    
    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for speech input once and return text"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Listening once...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # Convert to text
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.info("Timeout waiting for speech input")
            return None
        except sr.UnknownValueError:
            logger.info("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in listen_once: {e}")
            return None
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available TTS voices"""
        if not self.tts_engine:
            return {}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                voice_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender,
                    'age': voice.age
                })
            
            return {
                'current_voice': self.tts_engine.getProperty('voice'),
                'available_voices': voice_info
            }
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return {}
    
    def set_voice(self, voice_id: str) -> bool:
        """Set specific TTS voice"""
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def set_speech_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', rate)
                logger.info(f"Speech rate set to: {rate} WPM")
            except Exception as e:
                logger.error(f"Error setting speech rate: {e}")
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        if self.tts_engine:
            try:
                volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
                self.tts_engine.setProperty('volume', volume)
                logger.info(f"Volume set to: {volume}")
            except Exception as e:
                logger.error(f"Error setting volume: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        logger.info("Speech engine cleaned up")

# Example usage
if __name__ == "__main__":
    def speech_callback(text):
        print(f"Callback received: {text}")
    
    engine = SpeechEngine()
    
    # Test TTS
    engine.speak("Hello, this is a test of the speech engine.")
    
    # Test speech recognition
    print("Please speak something...")
    text = engine.listen_once()
    if text:
        print(f"You said: {text}")
        engine.speak(f"You said: {text}")
    
    engine.cleanup()