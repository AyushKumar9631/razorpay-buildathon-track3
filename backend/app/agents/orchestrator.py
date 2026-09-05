"""
AI Agent Orchestrator using LangGraph.
This coordinates the multi-agent workflow for revenue recovery.
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.config import settings
from app.agents.prompts import (
    format_diagnosis_prompt,
    format_intervention_prompt,
    format_message_prompt,
    format_compliance_prompt
)
from app.agents.tools import (
    get_customer_history,
    get_transaction_details,
    calculate_risk_score,
    check_contact_frequency,
    log_audit_trail,
    get_similar_cases
)


# Define the state that flows through the graph
class AgentState(TypedDict):
    """State object that flows through the agent workflow."""
    # Input data
    risk_id: str
    risk_type: str
    transaction_id: str
    customer_id: str

    # Retrieved data
    transaction_data: dict
    customer_data: dict
    contact_history: dict
    similar_cases: list

    # Analysis results
    diagnosis: dict
    risk_score: float
    recommended_intervention: dict

    # Compliance
    compliance_check: dict
    approved: bool

    # Generated content
    message_content: dict

    # Execution
    intervention_id: str
    execution_result: dict

    # Audit
    audit_log: list

    # Messages for LLM
    messages: Annotated[Sequence[BaseMessage], "messages"]

    # Next action
    next_action: str


class RevenueRecoveryOrchestrator:
    """Main orchestrator for revenue recovery AI agents."""

    def __init__(self, db: Session):
        self.db = db

        # Initialize LLM based on provider
        if settings.LLM_PROVIDER == "groq":
            self.llm = ChatGroq(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.GROQ_API_KEY
            )
        else:  # openai
            self.llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY
            )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes (agents)
        workflow.add_node("gather_data", self.gather_data_node)
        workflow.add_node("diagnose", self.diagnose_node)
        workflow.add_node("select_intervention", self.select_intervention_node)
        workflow.add_node("check_compliance", self.check_compliance_node)
        workflow.add_node("generate_message", self.generate_message_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("log_audit", self.log_audit_node)

        # Define the flow
        workflow.set_entry_point("gather_data")

        workflow.add_edge("gather_data", "diagnose")
        workflow.add_edge("diagnose", "select_intervention")
        workflow.add_edge("select_intervention", "check_compliance")

        # Conditional edge after compliance check
        workflow.add_conditional_edges(
            "check_compliance",
            self.compliance_router,
            {
                "approved": "generate_message",
                "rejected": "log_audit",
                "escalate": "log_audit"
            }
        )

        workflow.add_edge("generate_message", "execute")
        workflow.add_edge("execute", "log_audit")
        workflow.add_edge("log_audit", END)

        return workflow.compile()

    def gather_data_node(self, state: AgentState) -> AgentState:
        """Gather all necessary data for analysis."""
        print(f"[Gather Data] Collecting data for risk {state['risk_id']}")

        # Get transaction details
        transaction_data = get_transaction_details(state['transaction_id'], self.db)

        # Get customer profile
        customer_data = get_customer_history(state['customer_id'], self.db)

        # Get contact history
        contact_history = check_contact_frequency(state['customer_id'], self.db)

        # Get similar cases for learning
        similar_cases = get_similar_cases(
            state['risk_type'],
            customer_data.get('tier', 'standard'),
            self.db
        )

        # Calculate risk score
        risk_score = calculate_risk_score(
            customer_data,
            transaction_data,
            state['risk_type']
        )

        state['transaction_data'] = transaction_data
        state['customer_data'] = customer_data
        state['contact_history'] = contact_history
        state['similar_cases'] = similar_cases
        state['risk_score'] = risk_score
        state['audit_log'] = state.get('audit_log', [])
        state['audit_log'].append({
            "step": "gather_data",
            "timestamp": datetime.utcnow().isoformat(),
            "data_collected": True
        })

        return state

    def diagnose_node(self, state: AgentState) -> AgentState:
        """Diagnose the root cause using AI."""
        print(f"[Diagnose] Analyzing root cause for {state['risk_type']}")

        # Format prompt
        prompt = format_diagnosis_prompt(
            state['transaction_data'],
            state['customer_data'],
            state['risk_type']
        )

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            diagnosis = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            diagnosis = {
                "root_cause_category": "technical",
                "severity": "medium",
                "recovery_probability": state['risk_score'],
                "immediate_action": "contact_customer",
                "reasoning": response.content,
                "key_factors": []
            }

        state['diagnosis'] = diagnosis
        state['messages'] = messages + [response]
        state['audit_log'].append({
            "step": "diagnose",
            "timestamp": datetime.utcnow().isoformat(),
            "diagnosis": diagnosis
        })

        return state

    def select_intervention_node(self, state: AgentState) -> AgentState:
        """Select optimal intervention strategy using AI."""
        print(f"[Select Intervention] Choosing best strategy")

        # Format prompt
        prompt = format_intervention_prompt(
            state['diagnosis'],
            state['customer_data'],
            state['contact_history'],
            state['similar_cases']
        )

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            recommendation = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback
            recommendation = {
                "recommended_intervention": "email_with_update_link",
                "strategy": "immediate_contact",
                "channel": "email",
                "timing": "immediate",
                "priority": state['diagnosis'].get('severity', 'medium'),
                "reasoning": response.content,
                "expected_success_rate": state['risk_score'],
                "alternative": "sms_reminder"
            }

        state['recommended_intervention'] = recommendation
        state['messages'] = state['messages'] + messages + [response]
        state['audit_log'].append({
            "step": "select_intervention",
            "timestamp": datetime.utcnow().isoformat(),
            "recommendation": recommendation
        })

        return state

    def check_compliance_node(self, state: AgentState) -> AgentState:
        """Check compliance rules before execution."""
        print(f"[Compliance Check] Validating intervention")

        # Format prompt
        prompt = format_compliance_prompt(
            state['recommended_intervention'],
            state['customer_data'],
            state['contact_history']
        )

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            compliance_check = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback - manual rules check
            contact_limit_reached = state['contact_history'].get('limit_reached', False)
            compliance_check = {
                "compliant": not contact_limit_reached,
                "violations": ["contact_frequency_limit"] if contact_limit_reached else [],
                "warnings": [],
                "required_actions": [],
                "approved": not contact_limit_reached,
                "reasoning": response.content
            }

        state['compliance_check'] = compliance_check
        state['approved'] = compliance_check.get('approved', False)
        state['messages'] = state['messages'] + messages + [response]
        state['audit_log'].append({
            "step": "check_compliance",
            "timestamp": datetime.utcnow().isoformat(),
            "compliance_check": compliance_check,
            "approved": state['approved']
        })

        return state

    def compliance_router(self, state: AgentState) -> Literal["approved", "rejected", "escalate"]:
        """Route based on compliance check result."""
        if not state['approved']:
            violations = state['compliance_check'].get('violations', [])
            if any('escalate' in v.lower() for v in violations):
                return "escalate"
            return "rejected"
        return "approved"

    def generate_message_node(self, state: AgentState) -> AgentState:
        """Generate personalized message content using AI."""
        print(f"[Generate Message] Creating personalized content")

        customer_data = state['customer_data']
        intervention = state['recommended_intervention']

        # Create situation summary
        situation = f"Payment of {state['transaction_data'].get('amount')} failed. " \
                   f"Reason: {state['transaction_data'].get('failure_reason', 'Unknown')}. " \
                   f"Recovery probability: {state['diagnosis'].get('recovery_probability', 50)}%"

        # Format prompt
        prompt = format_message_prompt(
            customer_name=customer_data.get('name', 'Valued Customer'),
            customer_tier=customer_data.get('tier', 'standard'),
            relationship_length="long-term" if customer_data.get('total_transactions', 0) > 10 else "new",
            situation_summary=situation,
            intervention_type=intervention['recommended_intervention'],
            channel=intervention['channel'],
            use_hinglish=False  # Can be enabled based on customer preferences
        )

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            message_content = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback
            message_content = {
                "subject": "Action Required: Update Your Payment Information",
                "body": response.content,
                "cta": "Update Now",
                "tone": "friendly",
                "language": "english"
            }

        state['message_content'] = message_content
        state['messages'] = state['messages'] + messages + [response]
        state['audit_log'].append({
            "step": "generate_message",
            "timestamp": datetime.utcnow().isoformat(),
            "message_generated": True
        })

        return state

    def execute_node(self, state: AgentState) -> AgentState:
        """Execute the intervention (placeholder - actual execution in Phase 5)."""
        print(f"[Execute] Running intervention: {state['recommended_intervention']['recommended_intervention']}")

        # For now, simulate execution
        # In Phase 5, this will actually send emails, trigger retries, etc.
        execution_result = {
            "status": "executed",
            "intervention_type": state['recommended_intervention']['recommended_intervention'],
            "channel": state['recommended_intervention']['channel'],
            "executed_at": datetime.utcnow().isoformat(),
            "message_content": state.get('message_content', {}),
            "simulated": True  # Will be False when actually implemented
        }

        state['execution_result'] = execution_result
        state['audit_log'].append({
            "step": "execute",
            "timestamp": datetime.utcnow().isoformat(),
            "execution_result": execution_result
        })

        return state

    def log_audit_node(self, state: AgentState) -> AgentState:
        """Log complete audit trail to database."""
        print(f"[Audit] Logging complete workflow")

        # Log to database
        log_audit_trail(
            entity_type="risk",
            entity_id=state['risk_id'],
            action="ai_agent_workflow_complete",
            actor="ai_agent_orchestrator",
            details={
                "diagnosis": state.get('diagnosis', {}),
                "recommended_intervention": state.get('recommended_intervention', {}),
                "compliance_check": state.get('compliance_check', {}),
                "execution_result": state.get('execution_result', {}),
                "workflow_steps": len(state.get('audit_log', []))
            },
            compliance_check=state.get('compliance_check', {}),
            db=self.db
        )

        state['audit_log'].append({
            "step": "log_audit",
            "timestamp": datetime.utcnow().isoformat(),
            "audit_logged": True
        })

        return state

    def run(self, risk_id: str, risk_type: str, transaction_id: str, customer_id: str) -> dict:
        """Run the complete agent workflow."""
        print(f"\n{'='*60}")
        print(f"Starting AI Agent Workflow")
        print(f"Risk ID: {risk_id}")
        print(f"Risk Type: {risk_type}")
        print(f"{'='*60}\n")

        # Initialize state
        initial_state = AgentState(
            risk_id=risk_id,
            risk_type=risk_type,
            transaction_id=transaction_id,
            customer_id=customer_id,
            transaction_data={},
            customer_data={},
            contact_history={},
            similar_cases=[],
            diagnosis={},
            risk_score=0.0,
            recommended_intervention={},
            compliance_check={},
            approved=False,
            message_content={},
            intervention_id="",
            execution_result={},
            audit_log=[],
            messages=[],
            next_action=""
        )

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        print(f"\n{'='*60}")
        print(f"AI Agent Workflow Complete")
        print(f"Steps Executed: {len(final_state['audit_log'])}")
        print(f"Approved: {final_state['approved']}")
        print(f"{'='*60}\n")

        return {
            "risk_id": risk_id,
            "diagnosis": final_state.get('diagnosis', {}),
            "recommended_intervention": final_state.get('recommended_intervention', {}),
            "compliance_check": final_state.get('compliance_check', {}),
            "approved": final_state.get('approved', False),
            "execution_result": final_state.get('execution_result', {}),
            "audit_log": final_state.get('audit_log', [])
        }
