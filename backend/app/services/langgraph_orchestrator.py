"""
LangGraph-based Multi-Agent Orchestration Framework
Implements V7Labs-inspired finance agents with graph-based workflow coordination
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    """Types of specialized finance agents"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    RISK_ASSESSMENT = "risk_assessment"
    RECOMMENDATION = "recommendation"
    MONITORING = "monitoring"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class AgentState(TypedDict):
    """Shared state between agents in the workflow"""
    messages: List[BaseMessage]
    current_agent: str
    task_objective: str
    research_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    risk_assessments: Dict[str, Any]
    recommendations: Dict[str, Any]
    monitoring_alerts: List[Dict[str, Any]]
    workflow_status: str
    conflicts: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    execution_trace: List[Dict[str, Any]]
    next_agent: Optional[str]

@dataclass
class FinanceAgent:
    """Base class for specialized finance agents"""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    llm: ChatOpenAI
    tools: List[BaseTool]
    confidence_threshold: float = 0.7

    async def execute(self, state: AgentState) -> AgentState:
        """Execute agent-specific financial analysis tasks"""
        logger.info(f"Agent {self.name} ({self.agent_type}) executing task")

        # Add execution trace
        trace_entry = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "task_objective": state["task_objective"]
        }
        state["execution_trace"].append(trace_entry)

        # Update current agent
        state["current_agent"] = self.agent_id

        # Execute agent-specific logic based on type
        if self.agent_type == AgentType.RESEARCH:
            return await self._research_execute(state)
        elif self.agent_type == AgentType.ANALYSIS:
            return await self._analysis_execute(state)
        elif self.agent_type == AgentType.RISK_ASSESSMENT:
            return await self._risk_execute(state)
        elif self.agent_type == AgentType.RECOMMENDATION:
            return await self._recommendation_execute(state)
        elif self.agent_type == AgentType.MONITORING:
            return await self._monitoring_execute(state)

        return state

    async def _research_execute(self, state: AgentState) -> AgentState:
        """Research agent: Gather financial data and market intelligence"""
        logger.info("Executing research agent workflow")

        system_prompt = """You are a specialized financial research agent. Your task is to gather comprehensive
        market data, financial metrics, and relevant intelligence for the given objective. Focus on:
        - Market data collection and validation
        - Company financials and fundamentals
        - Industry trends and sector analysis
        - News sentiment and market intelligence
        - Regulatory and compliance information

        Provide structured, factual data with confidence scores and source citations."""

        messages = [SystemMessage(content=system_prompt)] + state["messages"]

        # Execute LLM reasoning
        response = await self.llm.ainvoke(messages)

        # Parse and structure research data
        research_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "objective": state["task_objective"],
            "findings": response.content,
            "confidence_score": 0.85,  # Would be calculated based on data quality
            "sources": ["market_data", "financial_reports", "news_feeds"],
            "data_quality": "high"
        }

        state["research_data"][self.agent_id] = research_data
        state["messages"].append(AIMessage(content=f"Research completed: {response.content}"))

        # Determine next agent based on workflow logic
        state["next_agent"] = "analysis_agent"

        return state

    async def _analysis_execute(self, state: AgentState) -> AgentState:
        """Analysis agent: Perform fundamental, technical, and quantitative analysis"""
        logger.info("Executing analysis agent workflow")

        system_prompt = """You are a specialized financial analysis agent. Using the research data provided,
        perform comprehensive financial analysis including:
        - Fundamental analysis (valuation, ratios, growth metrics)
        - Technical analysis (trends, patterns, indicators)
        - Quantitative modeling and statistical analysis
        - Comparative analysis against peers and benchmarks
        - Scenario analysis and sensitivity testing

        Provide detailed analysis with quantified insights and confidence intervals."""

        # Include research data in context
        research_context = json.dumps(state["research_data"], indent=2)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research Data:\n{research_context}"),
        ] + state["messages"]

        response = await self.llm.ainvoke(messages)

        analysis_results = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": ["fundamental", "technical", "quantitative"],
            "findings": response.content,
            "confidence_score": 0.82,
            "key_metrics": {
                "valuation_score": 0.75,
                "technical_score": 0.68,
                "growth_potential": 0.72
            },
            "recommendations": []
        }

        state["analysis_results"][self.agent_id] = analysis_results
        state["messages"].append(AIMessage(content=f"Analysis completed: {response.content}"))

        state["next_agent"] = "risk_assessment_agent"

        return state

    async def _risk_execute(self, state: AgentState) -> AgentState:
        """Risk assessment agent: Evaluate portfolio, market, and operational risks"""
        logger.info("Executing risk assessment agent workflow")

        system_prompt = """You are a specialized financial risk assessment agent. Evaluate all risk factors including:
        - Market risk (volatility, correlation, beta analysis)
        - Credit risk (default probability, credit quality)
        - Liquidity risk (market depth, trading volume)
        - Operational risk (company-specific factors)
        - Regulatory risk (compliance, policy changes)
        - Systemic risk (macro-economic factors)

        Provide quantified risk scores, risk-adjusted metrics, and mitigation strategies."""

        # Include previous agent outputs
        context_data = {
            "research": state["research_data"],
            "analysis": state["analysis_results"]
        }
        context = json.dumps(context_data, indent=2)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analysis Context:\n{context}"),
        ] + state["messages"]

        response = await self.llm.ainvoke(messages)

        risk_assessment = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_categories": ["market", "credit", "liquidity", "operational"],
            "findings": response.content,
            "overall_risk_score": 0.65,
            "risk_breakdown": {
                "market_risk": 0.70,
                "credit_risk": 0.45,
                "liquidity_risk": 0.55,
                "operational_risk": 0.60
            },
            "mitigation_strategies": []
        }

        state["risk_assessments"][self.agent_id] = risk_assessment
        state["messages"].append(AIMessage(content=f"Risk assessment completed: {response.content}"))

        state["next_agent"] = "recommendation_agent"

        return state

    async def _recommendation_execute(self, state: AgentState) -> AgentState:
        """Recommendation agent: Synthesize findings into actionable investment advice"""
        logger.info("Executing recommendation agent workflow")

        system_prompt = """You are a specialized financial recommendation agent. Synthesize all previous analysis into
        clear, actionable investment recommendations including:
        - Investment thesis and rationale
        - Specific buy/sell/hold recommendations
        - Target prices and time horizons
        - Portfolio allocation suggestions
        - Risk-adjusted return expectations
        - Key catalysts and monitoring points

        Provide confident recommendations with supporting evidence and dissenting views."""

        # Compile all agent outputs
        full_context = {
            "research": state["research_data"],
            "analysis": state["analysis_results"],
            "risk": state["risk_assessments"],
            "objective": state["task_objective"]
        }
        context = json.dumps(full_context, indent=2)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Complete Analysis Context:\n{context}"),
        ] + state["messages"]

        response = await self.llm.ainvoke(messages)

        recommendation = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendation_type": "investment_advice",
            "findings": response.content,
            "confidence_score": 0.88,
            "recommendation": "BUY",  # Would be extracted from LLM response
            "target_price": 150.00,  # Would be extracted from LLM response
            "time_horizon": "12_months",
            "risk_rating": "MODERATE",
            "supporting_evidence": [],
            "dissenting_views": []
        }

        state["recommendations"][self.agent_id] = recommendation
        state["messages"].append(AIMessage(content=f"Recommendation completed: {response.content}"))

        state["workflow_status"] = WorkflowStatus.COMPLETED.value
        state["next_agent"] = None

        return state

    async def _monitoring_execute(self, state: AgentState) -> AgentState:
        """Monitoring agent: Continuous surveillance and alert generation"""
        logger.info("Executing monitoring agent workflow")

        # Monitoring agent runs continuously, not part of main workflow
        monitoring_alert = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": "market_change",
            "severity": "medium",
            "message": "Market volatility increased by 15% in target sector",
            "action_required": False
        }

        state["monitoring_alerts"].append(monitoring_alert)
        return state

class LangGraphOrchestrator:
    """Main orchestration engine for multi-agent financial workflows"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.agents: Dict[str, FinanceAgent] = {}
        self.workflows: Dict[str, StateGraph] = {}
        self.memory = MemorySaver()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    def register_agent(self, agent: FinanceAgent):
        """Register a specialized finance agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_type})")

    def create_financial_workflow(self, workflow_id: str) -> StateGraph:
        """Create a graph-based workflow for financial analysis"""

        def route_next_agent(state: AgentState) -> str:
            """Route to next agent based on workflow logic"""
            next_agent = state.get("next_agent")
            if next_agent:
                return next_agent
            return END

        # Create workflow graph
        workflow = StateGraph(AgentState)

        # Add agent nodes
        workflow.add_node("research_agent", self._execute_research_agent)
        workflow.add_node("analysis_agent", self._execute_analysis_agent)
        workflow.add_node("risk_assessment_agent", self._execute_risk_agent)
        workflow.add_node("recommendation_agent", self._execute_recommendation_agent)

        # Define workflow edges
        workflow.add_edge("research_agent", "analysis_agent")
        workflow.add_edge("analysis_agent", "risk_assessment_agent")
        workflow.add_edge("risk_assessment_agent", "recommendation_agent")
        workflow.add_edge("recommendation_agent", END)

        # Set entry point
        workflow.set_entry_point("research_agent")

        # Compile with checkpointer for persistence
        compiled_workflow = workflow.compile(checkpointer=self.memory)

        self.workflows[workflow_id] = compiled_workflow
        return compiled_workflow

    async def _execute_research_agent(self, state: AgentState) -> AgentState:
        """Execute research agent"""
        agent = self.agents.get("research_agent")
        if agent:
            return await agent.execute(state)
        return state

    async def _execute_analysis_agent(self, state: AgentState) -> AgentState:
        """Execute analysis agent"""
        agent = self.agents.get("analysis_agent")
        if agent:
            return await agent.execute(state)
        return state

    async def _execute_risk_agent(self, state: AgentState) -> AgentState:
        """Execute risk assessment agent"""
        agent = self.agents.get("risk_assessment_agent")
        if agent:
            return await agent.execute(state)
        return state

    async def _execute_recommendation_agent(self, state: AgentState) -> AgentState:
        """Execute recommendation agent"""
        agent = self.agents.get("recommendation_agent")
        if agent:
            return await agent.execute(state)
        return state

    async def execute_workflow(
        self,
        workflow_id: str,
        task_objective: str,
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """Execute a financial analysis workflow"""

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Initialize workflow state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=task_objective)],
            "current_agent": "",
            "task_objective": task_objective,
            "research_data": {},
            "analysis_results": {},
            "risk_assessments": {},
            "recommendations": {},
            "monitoring_alerts": [],
            "workflow_status": WorkflowStatus.RUNNING.value,
            "conflicts": [],
            "decision_points": [],
            "execution_trace": [],
            "next_agent": None
        }

        workflow = self.workflows[workflow_id]
        config = {"configurable": {"thread_id": session_id}}

        try:
            # Execute workflow
            logger.info(f"Starting workflow {workflow_id} for objective: {task_objective}")
            result = await workflow.ainvoke(initial_state, config)

            # Store workflow results
            self.active_workflows[session_id] = {
                "workflow_id": workflow_id,
                "status": result["workflow_status"],
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise

    def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        return self.active_workflows.get(session_id, {})

    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered agents"""
        return {
            agent_id: agent.capabilities
            for agent_id, agent in self.agents.items()
        }

# Factory function to create configured orchestrator
def create_financial_orchestrator(openai_api_key: str) -> LangGraphOrchestrator:
    """Create a fully configured financial analysis orchestrator"""

    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="gpt-4o",
        temperature=0.1,
        max_tokens=4000
    )

    orchestrator = LangGraphOrchestrator(llm)

    # Create and register specialized finance agents
    research_agent = FinanceAgent(
        agent_id="research_agent",
        agent_type=AgentType.RESEARCH,
        name="Financial Research Agent",
        description="Specialized in market data gathering and financial intelligence",
        capabilities=[
            "market_data_collection",
            "financial_metrics_analysis",
            "news_sentiment_analysis",
            "regulatory_intelligence",
            "competitor_analysis"
        ],
        llm=llm,
        tools=[]
    )

    analysis_agent = FinanceAgent(
        agent_id="analysis_agent",
        agent_type=AgentType.ANALYSIS,
        name="Financial Analysis Agent",
        description="Specialized in fundamental, technical, and quantitative analysis",
        capabilities=[
            "fundamental_analysis",
            "technical_analysis",
            "quantitative_modeling",
            "valuation_analysis",
            "scenario_analysis"
        ],
        llm=llm,
        tools=[]
    )

    risk_agent = FinanceAgent(
        agent_id="risk_assessment_agent",
        agent_type=AgentType.RISK_ASSESSMENT,
        name="Risk Assessment Agent",
        description="Specialized in comprehensive risk evaluation",
        capabilities=[
            "market_risk_analysis",
            "credit_risk_assessment",
            "liquidity_risk_evaluation",
            "operational_risk_analysis",
            "regulatory_risk_assessment"
        ],
        llm=llm,
        tools=[]
    )

    recommendation_agent = FinanceAgent(
        agent_id="recommendation_agent",
        agent_type=AgentType.RECOMMENDATION,
        name="Investment Recommendation Agent",
        description="Specialized in generating actionable investment advice",
        capabilities=[
            "investment_thesis_development",
            "buy_sell_recommendations",
            "portfolio_optimization",
            "target_price_analysis",
            "risk_adjusted_returns"
        ],
        llm=llm,
        tools=[]
    )

    monitoring_agent = FinanceAgent(
        agent_id="monitoring_agent",
        agent_type=AgentType.MONITORING,
        name="Market Monitoring Agent",
        description="Specialized in continuous market surveillance",
        capabilities=[
            "real_time_monitoring",
            "alert_generation",
            "threshold_tracking",
            "anomaly_detection",
            "trend_identification"
        ],
        llm=llm,
        tools=[]
    )

    # Register all agents
    orchestrator.register_agent(research_agent)
    orchestrator.register_agent(analysis_agent)
    orchestrator.register_agent(risk_agent)
    orchestrator.register_agent(recommendation_agent)
    orchestrator.register_agent(monitoring_agent)

    # Create default financial analysis workflow
    orchestrator.create_financial_workflow("default_financial_analysis")

    logger.info("Financial orchestrator created with 5 specialized agents")
    return orchestrator