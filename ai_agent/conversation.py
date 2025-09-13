#!/usr/bin/env python3
"""
RupeeQ AI Calling Agent - Conversation Manager
Handles the conversation flow based on the RupeeQ overdraft script
"""

import re
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallState(Enum):
    """Call conversation states"""
    GREETING = "greeting"
    IDENTITY_CONFIRMATION = "identity_confirmation"
    SCRIPT_INTRODUCTION = "script_introduction"
    RECORDING_NOTICE = "recording_notice"
    EMPLOYMENT_STATUS = "employment_status"
    SALARY_COLLECTION = "salary_collection"
    BENEFITS_EXPLANATION = "benefits_explanation"
    PERSONAL_DETAILS = "personal_details"
    ELIGIBILITY_CHECK = "eligibility_check"
    BUREAU_CONSENT = "bureau_consent"
    DOCUMENT_REQUIREMENTS = "document_requirements"
    OBJECTION_HANDLING = "objection_handling"
    CALL_CLOSING = "call_closing"
    ENDED = "ended"

class ConversationManager:
    """Manages the conversation flow for RupeeQ overdraft calls"""
    
    def __init__(self):
        self.current_state = CallState.GREETING
        self.customer_name = ""
        self.agent_name = ""
        self.language = "en-IN"
        self.customer_data = {}
        self.conversation_history = []
        self.objection_responses = self._load_objection_responses()
        self.script_messages = self._load_script_messages()
        self.state_transitions = self._setup_state_transitions()
        
    def _load_objection_responses(self) -> Dict[str, str]:
        """Load objection handling responses"""
        return {
            "no_need": "An Overdraft Facility is a great financial backup. There is no EMI, and you only pay interest on the amount used.",
            "existing_loan": "You can balance transfer your loan for better interest rates.",
            "interest_rate": "1.25% monthly, calculated on a reducing balance method.",
            "need_time": "Sure, but this offer is currently available for your profile. Can we call you back in the evening?",
            "cash_withdrawal": "Yes, you can transfer the Overdraft amount directly to your account.",
            "no_emi": "There is no EMI in an Overdraft, only interest on the utilized amount.",
            "recording_question": "This call is recorded for training and quality purposes to enhance our service.",
            "credit_card": "Credit card cash withdrawals have extra charges, whereas Overdrafts don't.",
            "reducing_balance": "Interest is applied on the remaining balance after each repayment.",
            "processing_fee": "Banks charge a one-time processing fee starting from 1%.",
            "inappropriate_language": "Sir/Madam, I am here to assist you professionally. Please maintain a respectful conversation.",
            "unclear_voice": "Sir/Madam, I am unable to hear you properly. Could you please check your network or speak a bit louder?"
        }
    
    def _load_script_messages(self) -> Dict[CallState, List[str]]:
        """Load script messages for each state"""
        return {
            CallState.GREETING: [
                "Greetings!! {customer_name} Main {agent_name} Baat kar raha hun on Behalf of Bajaj Finance Limited.",
                "Kaise hain Aap Sir/Mam?"
            ],
            CallState.SCRIPT_INTRODUCTION: [
                "{customer_name} Ji ye call meine aap ko kiya hain ek Unique Financial Back up Plan ke liye jo ki Personal Loan Nahi hain Balki ek Flexi Overdraft Facility hain jo ki specially design Ki Gayi hain Salaried employees ke liye."
            ],
            CallState.RECORDING_NOTICE: [
                "Sir/Mam..Aage badhne se pehle btana chahunga ki ye call training ya quality purpose k liye record ho rahi hai"
            ],
            CallState.EMPLOYMENT_STATUS: [
                "Sir Kya main Jaan Sakta Hun Aap Abhi Job Karte Hain Ya Apka apna Business Hain."
            ],
            CallState.SALARY_COLLECTION: [
                "Thank You for the information Sir, Mein Batana Chahunga is Flexi Overdraft ke Antargat Aap Apni Net Salary Ka 10 Se 24 guna tak Financial Backup Le Sakte Hain jisme aap Ko Monthly EMI nahi deni hain Sirf Byaj ( Interest ) Dena hain wo bhi us amount par jo ki aap use karte hain Aur Ye Facility apke pass agle 8 saalo tak rahegi.",
                "{customer_name} Ji agar aap Mind na kare to kya mein Jaan Sakta hun Aap ki Net Take home salary kitni Hogi After all deductions."
            ],
            CallState.BENEFITS_EXPLANATION: [
                "Dhanyawad Sir Jaisa apne bataya ki aap ki Monthly Net Salary {salary} Rupaye hain to aap 10 -22 lacs tak ka financial backup le sakte hain bina kissi security ke aur iss par Interest Rate Matr 1.25% monthly reducing method me hain example ke liye agar aap 100000 Rupees withdraw karte aap ki assign limit mein se aur 30 days ke liye use karte hain to aap ko 30 din ke liye Sirf 1250 rupees interest dena hoga who bhi jitna amount aap use kar rahe hain uspar na ki poore loan amount par.",
                "Aur Sir Ye 100000 Rupe aap Bajaj ko 30 din ke andar kabhi bhi lauta sakte hain. Kehne ka matlab yeh hain sir ki ap ko interest per day ke hisab se lagega aur utne din ke liye dena hoga jitney din ke liye aap funds ka istemal karenge",
                "{customer_name} Ji Ye Sukar App ko Kaisa Laga ?"
            ],
            CallState.PERSONAL_DETAILS: [
                "Sir Itna hi nahi Ye amount aap Jarurat padne par kitni bhi baar Withdraw kar sakte hain aur Kissi Bhi Purpose Ya emergency ke liye use kar sakte hain jaise ghar mein koi renovation Karwana ho / Ya koi Shadi Ho / Yaa ap ko kahi Investment Karna chahte Ho / Ya Bacho Ki Higher Studies ke liye bhi ye paise use kar sakte hain aur jab aap ke pass extra funds available ho to kabhi bhi repay back karke part payment facility ka laabh utha sakte hain aur apna monthly interest save kar sakte hain with no extra charges.",
                "{customer_name} Ji Age ki jankari dene se pehle Kya mein Jaan Sakta Hun App Private Sector Mein Job Karte Hain Ya Government Sector Mein",
                "{customer_name} Ji Kya aap apni Company ka Poora Naam Bata Sakte Hain.",
                "Sir/mam Iss Flexi Overdraft Facility Ki Eligibility Check Karne ke liye Kya Mein Jaan Sakta Hun Aapka Poora Naam As per Pan Card",
                "Sir Aap Ka Date of Birth Kya Hoga",
                "Sir aap Apna Poora Pan Card Number Bata Denge please",
                "Sir Aap abhi/ Presently Kiss City Mein Reh rahe hain, Iska Area Pincode Kya Hoga",
                "Aur Sir Apne Apni Company Ka Poora Name Mujhe Bataya Tha Yaha Apka Designation Kya Hoga",
                "Aur Jaisa Apne mujhe Bataya Tha apki Net Salary {salary} Monthly Hain."
            ],
            CallState.ELIGIBILITY_CHECK: [
                "{customer_name} Ji Saari Jankari Dene Ke liye Dhanyawad Mein Sir abhi Bajaj Ke portal mein aap ki exact eligibility check karne ja raha hun jiske antargat mein aap ka credit Score aur aap ki monthly obligation check kaunga jiske liye aap ko ek link bhej raha hun Jo aap ko Bajaj ki Taraf se ayega aap uspar apna go ahead de dijiyega. Sir Link Bhej Kar mein aap ko again 10-15 min mein call back karta hun I hope Sir Ye number aap ka whats app par bhi available hoga."
            ],
            CallState.BUREAU_CONSENT: [
                "Batana chahunga bank one time bureau report check karta hai jo ki minorly impact karta hai but timely apne repayments karne se ye recover ho jata hai."
            ],
            CallState.DOCUMENT_REQUIREMENTS: [
                "Required document list shared with the customer – (As per Bank )",
                "1. 3 Months bank statement",
                "2. Last 3 months salary slips", 
                "3. Aadhar/Pan card",
                "4. 1 photograph",
                "5. Address Proof"
            ],
            CallState.CALL_CLOSING: [
                "Sir/Ma'am batana chahunga main aapki details aage bank me forward kar raha hu eligibility check ka liye and uske baad mai apko 15-20 minute me wapas call karunga agge ki processiosng k liye.",
                "Thank You ! Sir/Ma'am",
                "Is OD se related Kya mai aur kisi prakaar se aapki sahayta kar sakta/sakti hoon?",
                "Apna kimti samay dene ke liye dhanyavaad aapka din shubh ho"
            ]
        }
    
    def _setup_state_transitions(self) -> Dict[CallState, List[CallState]]:
        """Setup valid state transitions"""
        return {
            CallState.GREETING: [CallState.SCRIPT_INTRODUCTION],
            CallState.SCRIPT_INTRODUCTION: [CallState.RECORDING_NOTICE],
            CallState.RECORDING_NOTICE: [CallState.EMPLOYMENT_STATUS],
            CallState.EMPLOYMENT_STATUS: [CallState.SALARY_COLLECTION],
            CallState.SALARY_COLLECTION: [CallState.BENEFITS_EXPLANATION],
            CallState.BENEFITS_EXPLANATION: [CallState.PERSONAL_DETAILS, CallState.OBJECTION_HANDLING],
            CallState.PERSONAL_DETAILS: [CallState.ELIGIBILITY_CHECK, CallState.OBJECTION_HANDLING],
            CallState.ELIGIBILITY_CHECK: [CallState.BUREAU_CONSENT, CallState.OBJECTION_HANDLING],
            CallState.BUREAU_CONSENT: [CallState.DOCUMENT_REQUIREMENTS, CallState.OBJECTION_HANDLING],
            CallState.DOCUMENT_REQUIREMENTS: [CallState.CALL_CLOSING, CallState.OBJECTION_HANDLING],
            CallState.OBJECTION_HANDLING: [CallState.BENEFITS_EXPLANATION, CallState.PERSONAL_DETAILS, CallState.ELIGIBILITY_CHECK, CallState.BUREAU_CONSENT, CallState.DOCUMENT_REQUIREMENTS, CallState.CALL_CLOSING],
            CallState.CALL_CLOSING: [CallState.ENDED]
        }
    
    def start_call(self, customer_name: str, agent_name: str, language: str = "en-IN"):
        """Start a new conversation"""
        self.customer_name = customer_name
        self.agent_name = agent_name
        self.language = language
        self.current_state = CallState.GREETING
        self.customer_data = {}
        self.conversation_history = []
        
        logger.info(f"Started call with {customer_name} by {agent_name}")
    
    def get_next_message(self) -> Optional[str]:
        """Get the next message based on current state"""
        if self.current_state not in self.script_messages:
            return None
        
        messages = self.script_messages[self.current_state]
        
        # Get the first message for the current state
        if messages:
            message = messages[0]
            # Format message with customer data
            try:
                formatted_message = message.format(
                    customer_name=self.customer_name,
                    agent_name=self.agent_name,
                    salary=self.customer_data.get('salary', '100000'),
                    company=self.customer_data.get('company', ''),
                    designation=self.customer_data.get('designation', '')
                )
            except KeyError:
                # If formatting fails, return the message as-is
                formatted_message = message
            
            # Add to conversation history
            self.conversation_history.append({
                'state': self.current_state.value,
                'message': formatted_message,
                'timestamp': datetime.now().isoformat()
            })
            
            return formatted_message
        
        return None
    
    def process_user_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Process user input and return appropriate response"""
        user_input_lower = user_input.lower().strip()
        
        # Add user input to conversation history
        self.conversation_history.append({
            'state': 'user_input',
            'message': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check for objections first
        objection_type = self._detect_objection(user_input_lower)
        if objection_type:
            response = self._handle_objection(objection_type)
            return {
                'message': response,
                'state': 'objection_handling'
            }
        
        # Process based on current state
        if self.current_state == CallState.GREETING:
            # Move to next state after greeting
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        elif self.current_state == CallState.SCRIPT_INTRODUCTION:
            # Move to recording notice
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        elif self.current_state == CallState.RECORDING_NOTICE:
            # Move to employment status
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        elif self.current_state == CallState.EMPLOYMENT_STATUS:
            return self._process_employment_status(user_input_lower)
        elif self.current_state == CallState.SALARY_COLLECTION:
            return self._process_salary_collection(user_input)
        elif self.current_state == CallState.PERSONAL_DETAILS:
            return self._process_personal_details(user_input)
        elif self.current_state == CallState.BENEFITS_EXPLANATION:
            return self._process_benefits_response(user_input_lower)
        else:
            # Default response for other states - move to next state
            self._transition_to_next_state()
            next_message = self.get_next_message()
            if next_message:
                return {
                    'message': next_message,
                    'state': self.current_state.value
                }
            else:
                return self._get_default_response()
    
    def _detect_objection(self, user_input: str) -> Optional[str]:
        """Detect if user input contains an objection"""
        objection_keywords = {
            "no_need": ["don't need", "not interested", "no need", "not required", "not necessary"],
            "existing_loan": ["already have", "existing loan", "ongoing loan", "current loan"],
            "interest_rate": ["rate of interest", "interest rate", "what is the rate"],
            "need_time": ["think", "time", "discuss", "family", "later"],
            "cash_withdrawal": ["withdraw cash", "cash withdrawal", "cash"],
            "no_emi": ["emi", "monthly payment", "installment"],
            "recording_question": ["recording", "recorded", "why recording"],
            "credit_card": ["credit card", "already have card"],
            "reducing_balance": ["reducing balance", "how interest calculated"],
            "processing_fee": ["processing fee", "charges", "fees"],
            "inappropriate_language": ["fuck", "shit", "damn", "bloody"],
            "unclear_voice": ["can't hear", "unclear", "speak louder", "network issue"]
        }
        
        for objection_type, keywords in objection_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                return objection_type
        
        return None
    
    def _handle_objection(self, objection_type: str) -> str:
        """Handle detected objection"""
        if objection_type in self.objection_responses:
            self.current_state = CallState.OBJECTION_HANDLING
            return self.objection_responses[objection_type]
        
        return "I understand your concern. Let me explain how this can benefit you."
    
    def _process_employment_status(self, user_input: str) -> Dict[str, Any]:
        """Process employment status response"""
        if any(word in user_input for word in ["job", "employed", "salary", "employee"]):
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        else:
            return {
                'message': "I understand. For this overdraft facility, we primarily work with salaried employees. Do you have any other questions?",
                'state': 'clarification'
            }
    
    def _process_salary_collection(self, user_input: str) -> Dict[str, Any]:
        """Process salary information"""
        # Extract salary amount from user input
        salary_match = re.search(r'(\d+)', user_input.replace(',', ''))
        if salary_match:
            salary = int(salary_match.group(1))
            self.customer_data['salary'] = salary
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        else:
            return {
                'message': "Could you please tell me your net take-home salary amount? For example, if it's 50,000 rupees, please say 'fifty thousand'.",
                'state': 'salary_clarification'
            }
    
    def _process_personal_details(self, user_input: str) -> Dict[str, Any]:
        """Process personal details collection"""
        # For demo purposes, we'll accept any input and move forward
        # In a real implementation, you'd validate and store specific details
        
        if self.current_state == CallState.PERSONAL_DETAILS:
            # Move to next state after collecting basic info
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        
        return self._get_default_response()
    
    def _process_benefits_response(self, user_input: str) -> Dict[str, Any]:
        """Process response to benefits explanation"""
        if any(word in user_input for word in ["good", "great", "nice", "interested", "yes"]):
            self._transition_to_next_state()
            return {
                'message': self.get_next_message(),
                'state': self.current_state.value
            }
        else:
            return {
                'message': "Let me explain more about how this can help you. You can use this facility for any emergency or investment purpose without any EMI burden.",
                'state': 'benefits_clarification'
            }
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Get default response for current state"""
        next_message = self.get_next_message()
        if next_message:
            return {
                'message': next_message,
                'state': self.current_state.value
            }
        
        return {
            'message': "Thank you for your response. Let me continue with the process.",
            'state': 'continuation'
        }
    
    def _transition_to_next_state(self):
        """Transition to the next valid state"""
        if self.current_state in self.state_transitions:
            valid_states = self.state_transitions[self.current_state]
            if valid_states:
                # For demo, move to the first valid state
                # In a real implementation, you'd have more sophisticated logic
                self.current_state = valid_states[0]
                logger.info(f"Transitioned to state: {self.current_state.value}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history
    
    def get_customer_data(self) -> Dict[str, Any]:
        """Get collected customer data"""
        return self.customer_data
    
    def get_current_state(self) -> CallState:
        """Get current conversation state"""
        return self.current_state
    
    def end_call(self, outcome: str = "unknown"):
        """End the conversation"""
        self.current_state = CallState.ENDED
        self.conversation_history.append({
            'state': 'call_ended',
            'message': f'Call ended with outcome: {outcome}',
            'timestamp': datetime.now().isoformat()
        })
        logger.info(f"Call ended with outcome: {outcome}")

# Example usage and testing
if __name__ == "__main__":
    # Test the conversation manager
    cm = ConversationManager()
    cm.start_call("Yogesh Kumar", "Rahul", "en-IN")
    
    print("Starting conversation test...")
    
    # Test greeting
    message = cm.get_next_message()
    print(f"Agent: {message}")
    
    # Test employment status
    cm.process_user_input("I work in a job")
    message = cm.get_next_message()
    print(f"Agent: {message}")
    
    # Test salary collection
    cm.process_user_input("My salary is 100000 rupees")
    message = cm.get_next_message()
    print(f"Agent: {message}")
    
    print("Conversation test completed.")

