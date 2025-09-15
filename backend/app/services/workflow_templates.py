"""
Workflow Templates for Common Financial Analysis Patterns
Pre-built agent collaboration patterns for financial use cases
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.services.langgraph_orchestrator import AgentState, FinanceAgent, AgentType

logger = logging.getLogger(__name__)

class TemplateType(str, Enum):
    """Types of workflow templates"""
    DUE_DILIGENCE = "due_diligence"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_ASSESSMENT = "risk_assessment"
    SECTOR_ANALYSIS = "sector_analysis"
    ESG_ANALYSIS = "esg_analysis"
    MERGER_ANALYSIS = "merger_analysis"
    CREDIT_ANALYSIS = "credit_analysis"
    MARKET_ENTRY = "market_entry"

@dataclass
class WorkflowTemplate:
    """Workflow template definition"""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    agent_sequence: List[str]
    required_inputs: List[str]
    expected_outputs: List[str]
    estimated_duration: str
    complexity_level: str
    use_cases: List[str]

class FinancialWorkflowTemplates:
    """Factory for creating pre-configured financial analysis workflows"""

    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize all workflow templates"""

        # Due Diligence Template
        self.templates["due_diligence"] = WorkflowTemplate(
            template_id="due_diligence",
            name="Due Diligence Investigation",
            description="Comprehensive due diligence workflow for acquisition analysis",
            template_type=TemplateType.DUE_DILIGENCE,
            agent_sequence=["research_agent", "analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["target_company", "acquisition_parameters", "valuation_criteria"],
            expected_outputs=["financial_health_report", "risk_profile", "valuation_range", "recommendation"],
            estimated_duration="15-25 minutes",
            complexity_level="high",
            use_cases=[
                "M&A due diligence",
                "Investment evaluation",
                "Strategic partnerships",
                "Vendor assessment"
            ]
        )

        # Portfolio Optimization Template
        self.templates["portfolio_optimization"] = WorkflowTemplate(
            template_id="portfolio_optimization",
            name="Portfolio Optimization",
            description="Asset allocation and portfolio optimization workflow",
            template_type=TemplateType.PORTFOLIO_OPTIMIZATION,
            agent_sequence=["analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["current_portfolio", "investment_objectives", "risk_tolerance", "constraints"],
            expected_outputs=["optimal_allocation", "risk_metrics", "expected_returns", "rebalancing_plan"],
            estimated_duration="8-12 minutes",
            complexity_level="medium",
            use_cases=[
                "Portfolio rebalancing",
                "Asset allocation",
                "Risk optimization",
                "Performance enhancement"
            ]
        )

        # Risk Assessment Template
        self.templates["comprehensive_risk_assessment"] = WorkflowTemplate(
            template_id="comprehensive_risk_assessment",
            name="Comprehensive Risk Assessment",
            description="Multi-faceted risk evaluation workflow",
            template_type=TemplateType.RISK_ASSESSMENT,
            agent_sequence=["research_agent", "risk_assessment_agent", "monitoring_agent"],
            required_inputs=["risk_scope", "evaluation_parameters", "monitoring_criteria"],
            expected_outputs=["risk_profile", "mitigation_strategies", "monitoring_plan", "alerts_config"],
            estimated_duration="10-15 minutes",
            complexity_level="medium",
            use_cases=[
                "Enterprise risk management",
                "Investment risk evaluation",
                "Regulatory compliance",
                "Crisis preparedness"
            ]
        )

        # Sector Analysis Template
        self.templates["sector_analysis"] = WorkflowTemplate(
            template_id="sector_analysis",
            name="Sector Analysis",
            description="Comprehensive sector and industry analysis workflow",
            template_type=TemplateType.SECTOR_ANALYSIS,
            agent_sequence=["research_agent", "analysis_agent", "recommendation_agent"],
            required_inputs=["sector_definition", "analysis_scope", "benchmarks"],
            expected_outputs=["sector_overview", "competitive_landscape", "growth_prospects", "investment_opportunities"],
            estimated_duration="12-18 minutes",
            complexity_level="medium",
            use_cases=[
                "Investment theme development",
                "Market research",
                "Competitive intelligence",
                "Strategic planning"
            ]
        )

        # ESG Analysis Template
        self.templates["esg_analysis"] = WorkflowTemplate(
            template_id="esg_analysis",
            name="ESG Analysis",
            description="Environmental, Social, and Governance analysis workflow",
            template_type=TemplateType.ESG_ANALYSIS,
            agent_sequence=["research_agent", "analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["esg_criteria", "sustainability_goals", "regulatory_requirements"],
            expected_outputs=["esg_score", "sustainability_assessment", "compliance_status", "improvement_recommendations"],
            estimated_duration="15-20 minutes",
            complexity_level="high",
            use_cases=[
                "Sustainable investing",
                "ESG compliance",
                "Impact measurement",
                "Stakeholder reporting"
            ]
        )

        # Merger Analysis Template
        self.templates["merger_analysis"] = WorkflowTemplate(
            template_id="merger_analysis",
            name="Merger & Acquisition Analysis",
            description="M&A transaction analysis and valuation workflow",
            template_type=TemplateType.MERGER_ANALYSIS,
            agent_sequence=["research_agent", "analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["merger_details", "synergy_assumptions", "valuation_methods"],
            expected_outputs=["synergy_analysis", "valuation_models", "integration_risks", "deal_recommendation"],
            estimated_duration="20-30 minutes",
            complexity_level="high",
            use_cases=[
                "M&A evaluation",
                "Synergy analysis",
                "Deal structuring",
                "Post-merger integration"
            ]
        )

        # Credit Analysis Template
        self.templates["credit_analysis"] = WorkflowTemplate(
            template_id="credit_analysis",
            name="Credit Analysis",
            description="Credit risk evaluation and lending decision workflow",
            template_type=TemplateType.CREDIT_ANALYSIS,
            agent_sequence=["research_agent", "analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["borrower_information", "loan_parameters", "credit_criteria"],
            expected_outputs=["credit_score", "default_probability", "loan_terms", "lending_recommendation"],
            estimated_duration="10-15 minutes",
            complexity_level="medium",
            use_cases=[
                "Loan underwriting",
                "Credit risk assessment",
                "Portfolio management",
                "Regulatory compliance"
            ]
        )

        # Market Entry Template
        self.templates["market_entry"] = WorkflowTemplate(
            template_id="market_entry",
            name="Market Entry Analysis",
            description="Market entry strategy and opportunity assessment workflow",
            template_type=TemplateType.MARKET_ENTRY,
            agent_sequence=["research_agent", "analysis_agent", "risk_assessment_agent", "recommendation_agent"],
            required_inputs=["target_market", "entry_strategy", "resource_constraints"],
            expected_outputs=["market_opportunity", "competitive_analysis", "entry_risks", "strategy_recommendation"],
            estimated_duration="18-25 minutes",
            complexity_level="high",
            use_cases=[
                "Geographic expansion",
                "Product launch",
                "Strategic investments",
                "Partnership evaluation"
            ]
        )

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get workflow template by ID"""
        return self.templates.get(template_id)

    def list_templates(self) -> List[WorkflowTemplate]:
        """List all available workflow templates"""
        return list(self.templates.values())

    def get_templates_by_type(self, template_type: TemplateType) -> List[WorkflowTemplate]:
        """Get templates filtered by type"""
        return [t for t in self.templates.values() if t.template_type == template_type]

    def create_workflow_from_template(
        self,
        template_id: str,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> Optional[StateGraph]:
        """Create a StateGraph workflow from template"""

        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template {template_id} not found")
            return None

        try:
            if template_id == "due_diligence":
                return self._create_due_diligence_workflow(agents, memory)
            elif template_id == "portfolio_optimization":
                return self._create_portfolio_optimization_workflow(agents, memory)
            elif template_id == "comprehensive_risk_assessment":
                return self._create_risk_assessment_workflow(agents, memory)
            elif template_id == "sector_analysis":
                return self._create_sector_analysis_workflow(agents, memory)
            elif template_id == "esg_analysis":
                return self._create_esg_analysis_workflow(agents, memory)
            elif template_id == "merger_analysis":
                return self._create_merger_analysis_workflow(agents, memory)
            elif template_id == "credit_analysis":
                return self._create_credit_analysis_workflow(agents, memory)
            elif template_id == "market_entry":
                return self._create_market_entry_workflow(agents, memory)
            else:
                logger.error(f"Workflow creation not implemented for template {template_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to create workflow from template {template_id}: {e}")
            return None

    def _create_due_diligence_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create due diligence workflow with enhanced investigation steps"""

        workflow = StateGraph(AgentState)

        # Enhanced due diligence flow
        workflow.add_node("research_agent", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("financial_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("operational_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("risk_assessment", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("valuation", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("final_recommendation", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        # Define workflow sequence
        workflow.add_edge("research_agent", "financial_analysis")
        workflow.add_edge("financial_analysis", "operational_analysis")
        workflow.add_edge("operational_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "valuation")
        workflow.add_edge("valuation", "final_recommendation")
        workflow.add_edge("final_recommendation", END)

        workflow.set_entry_point("research_agent")

        return workflow.compile(checkpointer=memory)

    def _create_portfolio_optimization_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create portfolio optimization workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("portfolio_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("risk_modeling", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("optimization", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("portfolio_analysis", "risk_modeling")
        workflow.add_edge("risk_modeling", "optimization")
        workflow.add_edge("optimization", END)

        workflow.set_entry_point("portfolio_analysis")

        return workflow.compile(checkpointer=memory)

    def _create_risk_assessment_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create comprehensive risk assessment workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("risk_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("risk_analysis", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("monitoring_setup", lambda state: self._execute_agent(agents["monitoring_agent"], state))

        workflow.add_edge("risk_research", "risk_analysis")
        workflow.add_edge("risk_analysis", "monitoring_setup")
        workflow.add_edge("monitoring_setup", END)

        workflow.set_entry_point("risk_research")

        return workflow.compile(checkpointer=memory)

    def _create_sector_analysis_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create sector analysis workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("sector_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("sector_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("investment_opportunities", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("sector_research", "sector_analysis")
        workflow.add_edge("sector_analysis", "investment_opportunities")
        workflow.add_edge("investment_opportunities", END)

        workflow.set_entry_point("sector_research")

        return workflow.compile(checkpointer=memory)

    def _create_esg_analysis_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create ESG analysis workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("esg_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("esg_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("esg_risk_assessment", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("esg_recommendations", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("esg_research", "esg_analysis")
        workflow.add_edge("esg_analysis", "esg_risk_assessment")
        workflow.add_edge("esg_risk_assessment", "esg_recommendations")
        workflow.add_edge("esg_recommendations", END)

        workflow.set_entry_point("esg_research")

        return workflow.compile(checkpointer=memory)

    def _create_merger_analysis_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create merger analysis workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("merger_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("synergy_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("integration_risks", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("deal_recommendation", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("merger_research", "synergy_analysis")
        workflow.add_edge("synergy_analysis", "integration_risks")
        workflow.add_edge("integration_risks", "deal_recommendation")
        workflow.add_edge("deal_recommendation", END)

        workflow.set_entry_point("merger_research")

        return workflow.compile(checkpointer=memory)

    def _create_credit_analysis_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create credit analysis workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("borrower_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("financial_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("credit_risk_assessment", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("lending_recommendation", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("borrower_research", "financial_analysis")
        workflow.add_edge("financial_analysis", "credit_risk_assessment")
        workflow.add_edge("credit_risk_assessment", "lending_recommendation")
        workflow.add_edge("lending_recommendation", END)

        workflow.set_entry_point("borrower_research")

        return workflow.compile(checkpointer=memory)

    def _create_market_entry_workflow(
        self,
        agents: Dict[str, FinanceAgent],
        memory: MemorySaver
    ) -> StateGraph:
        """Create market entry analysis workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("market_research", lambda state: self._execute_agent(agents["research_agent"], state))
        workflow.add_node("opportunity_analysis", lambda state: self._execute_agent(agents["analysis_agent"], state))
        workflow.add_node("entry_risk_assessment", lambda state: self._execute_agent(agents["risk_assessment_agent"], state))
        workflow.add_node("strategy_recommendation", lambda state: self._execute_agent(agents["recommendation_agent"], state))

        workflow.add_edge("market_research", "opportunity_analysis")
        workflow.add_edge("opportunity_analysis", "entry_risk_assessment")
        workflow.add_edge("entry_risk_assessment", "strategy_recommendation")
        workflow.add_edge("strategy_recommendation", END)

        workflow.set_entry_point("market_research")

        return workflow.compile(checkpointer=memory)

    async def _execute_agent(self, agent: FinanceAgent, state: AgentState) -> AgentState:
        """Execute agent with template-specific context"""
        return await agent.execute(state)

    def get_template_parameters(self, template_id: str) -> Dict[str, Any]:
        """Get template-specific parameters and configuration"""

        template = self.get_template(template_id)
        if not template:
            return {}

        # Template-specific parameter configurations
        parameter_configs = {
            "due_diligence": {
                "required_documents": ["financial_statements", "legal_documents", "operational_metrics"],
                "analysis_depth": "comprehensive",
                "valuation_methods": ["dcf", "comparable_companies", "precedent_transactions"],
                "risk_categories": ["financial", "operational", "market", "regulatory"]
            },
            "portfolio_optimization": {
                "optimization_method": "mean_variance",
                "constraints": ["sector_limits", "concentration_limits", "liquidity_requirements"],
                "rebalancing_frequency": "quarterly",
                "risk_metrics": ["var", "cvar", "tracking_error", "sharpe_ratio"]
            },
            "comprehensive_risk_assessment": {
                "risk_frameworks": ["var", "stress_testing", "scenario_analysis"],
                "monitoring_frequency": "daily",
                "alert_thresholds": "configurable",
                "reporting_format": "dashboard"
            }
        }

        return parameter_configs.get(template_id, {})

# Factory function
def create_workflow_templates() -> FinancialWorkflowTemplates:
    """Create workflow templates factory"""
    return FinancialWorkflowTemplates()