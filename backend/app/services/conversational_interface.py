"""
Conversational Interface with Voice Interaction Capabilities
Enhanced multi-modal conversation system for financial agents
"""
import asyncio
import logging
import base64
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import io

from fastapi import UploadFile
from pydantic import BaseModel, Field
import speech_recognition as sr
from gtts import gTTS
import pygame
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ConversationMode(str, Enum):
    """Types of conversation modes"""
    TEXT = "text"
    VOICE = "voice"
    MULTIMODAL = "multimodal"

class VoiceLanguage(str, Enum):
    """Supported voice languages"""
    ENGLISH = "en"
    FRENCH = "fr"
    SWAHILI = "sw"
    AMHARIC = "am"
    ARABIC = "ar"

@dataclass
class ConversationContext:
    """Conversation session context"""
    session_id: str
    user_id: Optional[str]
    mode: ConversationMode
    language: VoiceLanguage
    agent_preferences: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    workflow_context: Optional[Dict[str, Any]]
    created_at: datetime
    last_activity: datetime

class VoiceMessage(BaseModel):
    """Voice message model"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: VoiceLanguage = Field(default=VoiceLanguage.ENGLISH)
    format: str = Field(default="wav", description="Audio format")

class ConversationMessage(BaseModel):
    """Conversation message model"""
    session_id: str
    message_type: str = Field(..., description="text, voice, or system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationResponse(BaseModel):
    """Enhanced conversation response"""
    session_id: str
    response_text: str
    response_audio: Optional[str] = Field(None, description="Base64 encoded audio response")
    agent_type: str
    confidence_score: float
    suggested_actions: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    workflow_triggers: List[str] = Field(default_factory=list)
    visual_elements: Optional[Dict[str, Any]] = None

class VoiceProcessor:
    """Voice processing capabilities for speech-to-text and text-to-speech"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize pygame for audio playback
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except Exception as e:
            logger.warning(f"Audio playback disabled: {e}")
            self.audio_enabled = False

    async def speech_to_text(
        self,
        audio_data: bytes,
        language: VoiceLanguage = VoiceLanguage.ENGLISH
    ) -> str:
        """Convert speech audio to text"""
        try:
            # Convert bytes to AudioFile for speech_recognition
            audio_io = io.BytesIO(audio_data)

            with sr.AudioFile(audio_io) as source:
                audio = self.recognizer.record(source)

            # Use appropriate language code
            lang_codes = {
                VoiceLanguage.ENGLISH: "en-US",
                VoiceLanguage.FRENCH: "fr-FR",
                VoiceLanguage.SWAHILI: "sw-KE",
                VoiceLanguage.AMHARIC: "am-ET",
                VoiceLanguage.ARABIC: "ar-SA"
            }

            lang_code = lang_codes.get(language, "en-US")

            # Attempt Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio, language=lang_code)
                logger.info(f"Speech recognized: {text[:50]}...")
                return text
            except sr.RequestError:
                # Fallback to offline recognition
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.info(f"Offline speech recognized: {text[:50]}...")
                    return text
                except sr.RequestError:
                    return "Speech recognition failed - please try again"

        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return "Could not process audio input"

    async def text_to_speech(
        self,
        text: str,
        language: VoiceLanguage = VoiceLanguage.ENGLISH
    ) -> bytes:
        """Convert text to speech audio"""
        try:
            # Map voice languages to gTTS codes
            lang_codes = {
                VoiceLanguage.ENGLISH: "en",
                VoiceLanguage.FRENCH: "fr",
                VoiceLanguage.SWAHILI: "sw",
                VoiceLanguage.AMHARIC: "am",
                VoiceLanguage.ARABIC: "ar"
            }

            lang_code = lang_codes.get(language, "en")

            # Generate speech
            tts = gTTS(text=text, lang=lang_code, slow=False)

            # Save to BytesIO buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            return audio_buffer.getvalue()

        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            # Return empty bytes if TTS fails
            return b""

    async def play_audio(self, audio_data: bytes) -> bool:
        """Play audio data through speakers"""
        if not self.audio_enabled:
            return False

        try:
            # Save to temporary file and play
            temp_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            return True

        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False

class ConversationalInterface:
    """Main conversational interface with multi-modal capabilities"""

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client
        self.voice_processor = VoiceProcessor()
        self.active_sessions: Dict[str, ConversationContext] = {}
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        mode: ConversationMode = ConversationMode.TEXT,
        language: VoiceLanguage = VoiceLanguage.ENGLISH,
        agent_preferences: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """Create a new conversation session"""

        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            language=language,
            agent_preferences=agent_preferences or {},
            conversation_history=[],
            workflow_context=None,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        self.active_sessions[session_id] = context
        self.conversation_history[session_id] = []

        logger.info(f"Created conversation session {session_id} in {mode} mode")
        return context

    async def process_text_message(
        self,
        session_id: str,
        message: str,
        agent_type: Optional[str] = None
    ) -> ConversationResponse:
        """Process text-based conversation message"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        context = self.active_sessions[session_id]
        context.last_activity = datetime.utcnow()

        # Add user message to history
        user_message = ConversationMessage(
            session_id=session_id,
            message_type="text",
            content=message,
            timestamp=datetime.utcnow()
        )
        self.conversation_history[session_id].append(user_message)

        # Generate intelligent response based on context
        response_text = await self._generate_intelligent_response(
            message, context, agent_type
        )

        # Add agent response to history
        agent_message = ConversationMessage(
            session_id=session_id,
            message_type="text",
            content=response_text,
            agent_id=agent_type or "general",
            confidence_score=0.85,
            timestamp=datetime.utcnow()
        )
        self.conversation_history[session_id].append(agent_message)

        # Generate audio response if in voice mode
        response_audio = None
        if context.mode in [ConversationMode.VOICE, ConversationMode.MULTIMODAL]:
            audio_data = await self.voice_processor.text_to_speech(
                response_text, context.language
            )
            if audio_data:
                response_audio = base64.b64encode(audio_data).decode('utf-8')

        return ConversationResponse(
            session_id=session_id,
            response_text=response_text,
            response_audio=response_audio,
            agent_type=agent_type or "general",
            confidence_score=0.85,
            suggested_actions=self._generate_suggested_actions(message),
            follow_up_questions=self._generate_follow_up_questions(message),
            workflow_triggers=self._identify_workflow_triggers(message)
        )

    async def process_voice_message(
        self,
        session_id: str,
        voice_message: VoiceMessage,
        agent_type: Optional[str] = None
    ) -> ConversationResponse:
        """Process voice-based conversation message"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        context = self.active_sessions[session_id]

        # Convert voice to text
        audio_data = base64.b64decode(voice_message.audio_data)
        transcribed_text = await self.voice_processor.speech_to_text(
            audio_data, voice_message.language
        )

        # Process as text message
        response = await self.process_text_message(
            session_id, transcribed_text, agent_type
        )

        # Ensure voice response is included
        if not response.response_audio and context.mode == ConversationMode.VOICE:
            audio_data = await self.voice_processor.text_to_speech(
                response.response_text, context.language
            )
            if audio_data:
                response.response_audio = base64.b64encode(audio_data).decode('utf-8')

        return response

    async def _generate_intelligent_response(
        self,
        message: str,
        context: ConversationContext,
        agent_type: Optional[str] = None
    ) -> str:
        """Generate contextually aware response using OpenAI"""

        # Build conversation context
        recent_history = self.conversation_history[context.session_id][-10:]  # Last 10 messages
        history_text = "\n".join([
            f"{msg.message_type}: {msg.content}" for msg in recent_history
        ])

        # Create agent-specific system prompt
        system_prompt = self._get_agent_system_prompt(agent_type)

        # Add conversation context
        full_prompt = f"""
{system_prompt}

Previous conversation:
{history_text}

Current user message: {message}

Provide a helpful, contextually aware response. If the user is asking about financial analysis,
suggest relevant workflows or agent capabilities. Be concise but informative.
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI response generation failed: {e}")
            return self._get_fallback_response(message, agent_type)

    def _get_agent_system_prompt(self, agent_type: Optional[str]) -> str:
        """Get agent-specific system prompt"""

        prompts = {
            "research": """You are a Financial Research Agent specializing in market data gathering
            and financial intelligence. You help users find and analyze financial information,
            market trends, and company data.""",

            "analysis": """You are a Financial Analysis Agent specializing in fundamental,
            technical, and quantitative analysis. You help users understand financial metrics,
            valuation, and investment analysis.""",

            "risk_assessment": """You are a Risk Assessment Agent specializing in identifying
            and evaluating financial risks. You help users understand market risk, credit risk,
            and portfolio risk factors.""",

            "recommendation": """You are an Investment Recommendation Agent specializing in
            providing actionable investment advice. You synthesize analysis from other agents
            to provide clear recommendations.""",

            "monitoring": """You are a Market Monitoring Agent specializing in continuous
            surveillance and alerts. You help users track market changes and identify
            important developments."""
        }

        return prompts.get(agent_type, """You are a helpful financial AI assistant
        that can coordinate with specialized agents for research, analysis, risk assessment,
        recommendations, and monitoring.""")

    def _get_fallback_response(self, message: str, agent_type: Optional[str]) -> str:
        """Generate fallback response when OpenAI is unavailable"""

        message_lower = message.lower()

        if "analysis" in message_lower:
            return "I can help you with financial analysis. Would you like me to start a comprehensive analysis workflow?"
        elif "risk" in message_lower:
            return "I can assess financial risks for you. What specific risks would you like me to evaluate?"
        elif "recommendation" in message_lower:
            return "I can provide investment recommendations. What are you looking to invest in?"
        elif "research" in message_lower:
            return "I can help with financial research. What company or sector would you like me to research?"
        else:
            return "I'm here to help with financial analysis. You can ask me about research, analysis, risk assessment, or investment recommendations."

    def _generate_suggested_actions(self, message: str) -> List[str]:
        """Generate contextual action suggestions"""

        message_lower = message.lower()
        suggestions = []

        if any(word in message_lower for word in ["analyze", "analysis", "study"]):
            suggestions.extend([
                "Start comprehensive financial analysis",
                "Perform sector analysis",
                "Generate market report"
            ])

        if any(word in message_lower for word in ["risk", "danger", "threat"]):
            suggestions.extend([
                "Assess portfolio risk",
                "Evaluate market risk",
                "Generate risk report"
            ])

        if any(word in message_lower for word in ["buy", "sell", "invest", "recommend"]):
            suggestions.extend([
                "Get investment recommendations",
                "Optimize portfolio allocation",
                "Compare investment options"
            ])

        return suggestions[:3]  # Return top 3 suggestions

    def _generate_follow_up_questions(self, message: str) -> List[str]:
        """Generate relevant follow-up questions"""

        questions = [
            "What specific timeframe are you considering?",
            "What's your risk tolerance level?",
            "Are you looking at any particular sectors?",
            "Would you like me to include competitor analysis?",
            "Should I consider ESG factors in the analysis?"
        ]

        return questions[:3]  # Return top 3 questions

    def _identify_workflow_triggers(self, message: str) -> List[str]:
        """Identify potential workflow triggers from message"""

        message_lower = message.lower()
        triggers = []

        if "comprehensive" in message_lower or "full analysis" in message_lower:
            triggers.append("default_financial_analysis")

        if "due diligence" in message_lower:
            triggers.append("due_diligence")

        if "portfolio" in message_lower and "optimize" in message_lower:
            triggers.append("portfolio_optimization")

        if "monitor" in message_lower or "alert" in message_lower:
            triggers.append("risk_monitoring")

        return triggers

    async def stream_conversation(
        self,
        session_id: str,
        message: str,
        agent_type: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream conversation response for real-time interaction"""

        # Yield initial acknowledgment
        yield {
            "type": "acknowledgment",
            "content": "Processing your request...",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Simulate streaming response (would be actual streaming in production)
        response_parts = [
            "I understand you're asking about ",
            "financial analysis. Let me ",
            "gather the relevant information ",
            "and provide you with a comprehensive ",
            "response..."
        ]

        for i, part in enumerate(response_parts):
            await asyncio.sleep(0.5)  # Simulate processing time
            yield {
                "type": "partial_response",
                "content": part,
                "progress": (i + 1) / len(response_parts),
                "timestamp": datetime.utcnow().isoformat()
            }

        # Generate and yield final response
        final_response = await self.process_text_message(session_id, message, agent_type)

        yield {
            "type": "final_response",
            "content": final_response.response_text,
            "suggestions": final_response.suggested_actions,
            "follow_up_questions": final_response.follow_up_questions,
            "workflow_triggers": final_response.workflow_triggers,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information and statistics"""

        if session_id not in self.active_sessions:
            return None

        context = self.active_sessions[session_id]
        history = self.conversation_history.get(session_id, [])

        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "mode": context.mode.value,
            "language": context.language.value,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "message_count": len(history),
            "agent_preferences": context.agent_preferences,
            "workflow_context": context.workflow_context
        }

    async def cleanup_session(self, session_id: str) -> bool:
        """Clean up conversation session"""

        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

        logger.info(f"Cleaned up conversation session {session_id}")
        return True

# Factory function
def create_conversational_interface(openai_client: AsyncOpenAI) -> ConversationalInterface:
    """Create configured conversational interface"""
    return ConversationalInterface(openai_client)