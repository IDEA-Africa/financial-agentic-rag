"""
Enhanced Agentic RAG API endpoints
LangGraph-based multi-agent financial workflows with V7Labs-inspired capabilities
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.langgraph_orchestrator import (
    create_financial_orchestrator,
    LangGraphOrchestrator,
    AgentType,
    WorkflowStatus
)
from app.services.conversational_interface import (
    create_conversational_interface,
    ConversationalInterface,
    ConversationMode,
    VoiceLanguage,
    VoiceMessage,
    ConversationRequest,
    ConversationResponse
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agents", tags=["Enhanced Agentic RAG"])

# Global instances
_orchestrator: Optional[LangGraphOrchestrator] = None
_conversational_interface: Optional[ConversationalInterface] = None

def get_orchestrator() -> LangGraphOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        settings = get_settings()
        _orchestrator = create_financial_orchestrator(settings.openai_api_key)
    return _orchestrator

def get_conversational_interface() -> ConversationalInterface:
    """Get or create the global conversational interface instance"""
    global _conversational_interface
    if _conversational_interface is None:
        from openai import AsyncOpenAI
        settings = get_settings()
        openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        _conversational_interface = create_conversational_interface(openai_client)
    return _conversational_interface

# Request/Response Models
class FinancialAnalysisRequest(BaseModel):
    """Request model for financial analysis workflow"""
    objective: str = Field(..., description="Financial analysis objective or question")
    workflow_type: str = Field(default="default_financial_analysis", description="Type of workflow to execute")
    session_id: Optional[str] = Field(default=None, description="Session ID for workflow persistence")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Additional workflow parameters")

class AgentExecutionResponse(BaseModel):
    """Response model for agent execution results"""
    workflow_id: str
    session_id: str
    status: str
    objective: str
    agents_executed: List[str]
    research_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    risk_assessments: Dict[str, Any]
    recommendations: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    completed_at: Optional[str]

class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status"""
    session_id: str
    workflow_id: str
    status: str
    current_agent: Optional[str]
    progress_percentage: float
    execution_time_seconds: Optional[float]
    last_updated: str

class AgentCapabilitiesResponse(BaseModel):
    """Response model for agent capabilities"""
    agent_id: str
    agent_type: str
    name: str
    description: str
    capabilities: List[str]

class ConversationRequest(BaseModel):
    """Request model for conversational agent interaction"""
    message: str = Field(..., description="User message or question")
    session_id: str = Field(..., description="Conversation session ID")
    agent_type: Optional[str] = Field(default=None, description="Specific agent type to interact with")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context for the conversation")

class ConversationResponse(BaseModel):
    """Response model for conversational interaction"""
    session_id: str
    agent_response: str
    agent_type: str
    confidence_score: float
    suggestions: List[str]
    follow_up_questions: List[str]

# Main API Endpoints

@router.post("/analyze", response_model=AgentExecutionResponse)
async def execute_financial_analysis(
    request: FinancialAnalysisRequest,
    background_tasks: BackgroundTasks
) -> AgentExecutionResponse:
    """
    Execute a comprehensive financial analysis workflow using specialized agents

    This endpoint triggers a multi-agent workflow that includes:
    - Research agent: Data gathering and market intelligence
    - Analysis agent: Fundamental, technical, and quantitative analysis
    - Risk assessment agent: Comprehensive risk evaluation
    - Recommendation agent: Investment advice synthesis
    """
    try:
        orchestrator = get_orchestrator()

        # Generate session ID if not provided
        session_id = request.session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting financial analysis workflow for session: {session_id}")

        # Execute workflow
        result = await orchestrator.execute_workflow(
            workflow_id=request.workflow_type,
            task_objective=request.objective,
            session_id=session_id
        )

        # Extract agent execution information
        agents_executed = list(set([
            trace["agent_id"] for trace in result.get("execution_trace", [])
        ]))

        return AgentExecutionResponse(
            workflow_id=request.workflow_type,
            session_id=session_id,
            status=result.get("workflow_status", "unknown"),
            objective=request.objective,
            agents_executed=agents_executed,
            research_data=result.get("research_data", {}),
            analysis_results=result.get("analysis_results", {}),
            risk_assessments=result.get("risk_assessments", {}),
            recommendations=result.get("recommendations", {}),
            execution_trace=result.get("execution_trace", []),
            conflicts=result.get("conflicts", []),
            completed_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Financial analysis execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("/workflow/{session_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(session_id: str) -> WorkflowStatusResponse:
    """
    Get the current status of a running or completed workflow
    """
    try:
        orchestrator = get_orchestrator()
        workflow_data = orchestrator.get_workflow_status(session_id)

        if not workflow_data:
            raise HTTPException(status_code=404, detail=f"Workflow session {session_id} not found")

        # Calculate progress based on completed agents
        result = workflow_data.get("result", {})
        execution_trace = result.get("execution_trace", [])

        # Estimate progress (basic implementation)
        total_agents = 4  # research, analysis, risk, recommendation
        completed_agents = len(execution_trace)
        progress = min((completed_agents / total_agents) * 100, 100.0)

        return WorkflowStatusResponse(
            session_id=session_id,
            workflow_id=workflow_data.get("workflow_id", "unknown"),
            status=workflow_data.get("status", "unknown"),
            current_agent=result.get("current_agent"),
            progress_percentage=progress,
            execution_time_seconds=None,  # Would calculate from timestamps
            last_updated=workflow_data.get("completed_at", datetime.utcnow().isoformat())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities", response_model=List[AgentCapabilitiesResponse])
async def get_agent_capabilities() -> List[AgentCapabilitiesResponse]:
    """
    Get capabilities and descriptions of all available financial agents
    """
    try:
        orchestrator = get_orchestrator()
        capabilities = []

        for agent_id, agent in orchestrator.agents.items():
            capabilities.append(AgentCapabilitiesResponse(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type.value,
                name=agent.name,
                description=agent.description,
                capabilities=agent.capabilities
            ))

        return capabilities

    except Exception as e:
        logger.error(f"Failed to get agent capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation", response_model=ConversationResponse)
async def agent_conversation(request: ConversationRequest) -> ConversationResponse:
    """
    Interactive conversation with specific financial agents

    Enables natural language interaction with specialized agents for:
    - Clarifying analysis requirements
    - Discussing specific findings
    - Exploring alternative scenarios
    - Getting detailed explanations
    """
    try:
        orchestrator = get_orchestrator()

        # For now, provide a basic conversational response
        # This would be enhanced with actual agent conversation capabilities

        agent_type = request.agent_type or "general"

        # Simple response generation (would be enhanced with actual agent interaction)
        response_content = f"Thank you for your question: '{request.message}'. "

        if "analysis" in request.message.lower():
            response_content += "I can help you with financial analysis including fundamental, technical, and quantitative methods."
        elif "risk" in request.message.lower():
            response_content += "I can assess various risk factors including market, credit, liquidity, and operational risks."
        elif "recommendation" in request.message.lower():
            response_content += "I can provide investment recommendations based on comprehensive analysis and risk assessment."
        else:
            response_content += "I'm here to help with financial research, analysis, risk assessment, and recommendations."

        return ConversationResponse(
            session_id=request.session_id,
            agent_response=response_content,
            agent_type=agent_type,
            confidence_score=0.85,
            suggestions=[
                "Would you like me to perform a sector analysis?",
                "Should I assess the risk profile of specific securities?",
                "Would you like investment recommendations for your portfolio?"
            ],
            follow_up_questions=[
                "What specific companies or sectors are you interested in?",
                "What is your risk tolerance and investment timeline?",
                "Are there any specific metrics you'd like me to focus on?"
            ]
        )

    except Exception as e:
        logger.error(f"Conversation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/{session_id}/stream")
async def stream_workflow_progress(session_id: str):
    """
    Stream real-time updates of workflow execution progress

    Provides Server-Sent Events (SSE) for real-time workflow monitoring
    """
    async def generate_progress_updates():
        """Generate progress updates for streaming"""
        try:
            orchestrator = get_orchestrator()

            # In a real implementation, this would connect to actual workflow events
            # For now, simulate progress updates

            updates = [
                {"agent": "research", "status": "starting", "progress": 10},
                {"agent": "research", "status": "gathering_data", "progress": 25},
                {"agent": "research", "status": "completed", "progress": 30},
                {"agent": "analysis", "status": "starting", "progress": 35},
                {"agent": "analysis", "status": "analyzing", "progress": 60},
                {"agent": "analysis", "status": "completed", "progress": 70},
                {"agent": "risk_assessment", "status": "starting", "progress": 75},
                {"agent": "risk_assessment", "status": "completed", "progress": 85},
                {"agent": "recommendation", "status": "starting", "progress": 90},
                {"agent": "recommendation", "status": "completed", "progress": 100}
            ]

            for update in updates:
                yield f"data: {update}\n\n"
                await asyncio.sleep(0.5)  # Simulate real-time updates

        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return StreamingResponse(
        generate_progress_updates(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.post("/workflow/{workflow_id}/template")
async def create_workflow_template(
    workflow_id: str,
    template_data: Dict[str, Any]
) -> Dict[str, str]:
    """
    Create reusable workflow templates for common financial analysis patterns

    Templates can include:
    - Due diligence workflows
    - Portfolio optimization patterns
    - Risk assessment procedures
    - Sector analysis templates
    """
    try:
        # Template creation logic would be implemented here
        # For now, return a success response

        return {
            "workflow_id": workflow_id,
            "status": "template_created",
            "message": f"Workflow template {workflow_id} created successfully"
        }

    except Exception as e:
        logger.error(f"Template creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/templates")
async def list_workflow_templates() -> List[Dict[str, Any]]:
    """
    List available workflow templates
    """
    templates = [
        {
            "id": "default_financial_analysis",
            "name": "Comprehensive Financial Analysis",
            "description": "Full workflow including research, analysis, risk assessment, and recommendations",
            "agents": ["research", "analysis", "risk_assessment", "recommendation"],
            "estimated_duration": "5-10 minutes"
        },
        {
            "id": "due_diligence",
            "name": "Due Diligence Investigation",
            "description": "Deep investigation workflow for acquisition analysis",
            "agents": ["research", "analysis", "risk_assessment"],
            "estimated_duration": "10-15 minutes"
        },
        {
            "id": "portfolio_optimization",
            "name": "Portfolio Optimization",
            "description": "Asset allocation and portfolio optimization workflow",
            "agents": ["analysis", "risk_assessment", "recommendation"],
            "estimated_duration": "3-7 minutes"
        },
        {
            "id": "risk_monitoring",
            "name": "Risk Monitoring",
            "description": "Continuous risk surveillance and alert generation",
            "agents": ["monitoring", "risk_assessment"],
            "estimated_duration": "Continuous"
        }
    ]

    return templates

# Enhanced Conversational Interface Endpoints

@router.post("/conversation/session", response_model=Dict[str, Any])
async def create_conversation_session(
    session_id: str,
    user_id: Optional[str] = None,
    mode: str = "text",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Create a new conversation session with specified mode and language

    Supports:
    - Text conversations
    - Voice conversations with speech-to-text and text-to-speech
    - Multi-modal interactions
    - Multiple African languages
    """
    try:
        interface = get_conversational_interface()

        # Map string parameters to enums
        conversation_mode = ConversationMode(mode)
        voice_language = VoiceLanguage(language)

        context = await interface.create_session(
            session_id=session_id,
            user_id=user_id,
            mode=conversation_mode,
            language=voice_language
        )

        return {
            "session_id": session_id,
            "status": "created",
            "mode": mode,
            "language": language,
            "created_at": context.created_at.isoformat(),
            "capabilities": [
                "text_interaction",
                "voice_interaction" if mode in ["voice", "multimodal"] else None,
                "workflow_integration",
                "agent_coordination"
            ]
        }

    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/text", response_model=ConversationResponse)
async def text_conversation(request: ConversationRequest) -> ConversationResponse:
    """
    Process text-based conversation with financial agents

    Enhanced with:
    - Context-aware responses
    - Workflow trigger detection
    - Multi-agent coordination
    - Follow-up suggestions
    """
    try:
        interface = get_conversational_interface()

        response = await interface.process_text_message(
            session_id=request.session_id,
            message=request.message,
            agent_type=request.agent_type
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Text conversation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/voice", response_model=ConversationResponse)
async def voice_conversation(
    session_id: str,
    voice_message: VoiceMessage,
    agent_type: Optional[str] = None
) -> ConversationResponse:
    """
    Process voice-based conversation with speech-to-text and text-to-speech

    Features:
    - Multi-language speech recognition
    - Natural voice synthesis
    - Context preservation
    - Audio response generation
    """
    try:
        interface = get_conversational_interface()

        response = await interface.process_voice_message(
            session_id=session_id,
            voice_message=voice_message,
            agent_type=agent_type
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Voice conversation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{session_id}/stream")
async def stream_conversation(
    session_id: str,
    message: str,
    agent_type: Optional[str] = None
):
    """
    Stream real-time conversation responses

    Provides:
    - Real-time response generation
    - Progress indicators
    - Partial response updates
    - WebSocket-style interaction over HTTP
    """
    async def generate_conversation_stream():
        try:
            interface = get_conversational_interface()

            async for update in interface.stream_conversation(
                session_id=session_id,
                message=message,
                agent_type=agent_type
            ):
                yield f"data: {json.dumps(update)}\n\n"

        except Exception as e:
            error_update = {
                "type": "error",
                "content": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(error_update)}\n\n"

    return StreamingResponse(
        generate_conversation_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/conversation/{session_id}/info", response_model=Dict[str, Any])
async def get_conversation_info(session_id: str) -> Dict[str, Any]:
    """
    Get conversation session information and statistics
    """
    try:
        interface = get_conversational_interface()
        session_info = interface.get_session_info(session_id)

        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return session_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{session_id}")
async def cleanup_conversation_session(session_id: str) -> Dict[str, str]:
    """
    Clean up conversation session and free resources
    """
    try:
        interface = get_conversational_interface()
        success = await interface.cleanup_session(session_id)

        if success:
            return {"session_id": session_id, "status": "cleaned_up"}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for the enhanced agentic system
    """
    try:
        orchestrator = get_orchestrator()
        agent_count = len(orchestrator.agents)
        workflow_count = len(orchestrator.workflows)

        return {
            "status": "healthy",
            "agents_registered": agent_count,
            "workflows_available": workflow_count,
            "capabilities": ["research", "analysis", "risk_assessment", "recommendation", "monitoring"],
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }