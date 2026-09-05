"""
AI Agent Prompts - Templates for LLM interactions.
"""

DIAGNOSIS_PROMPT = """You are a revenue recovery specialist analyzing a failed transaction or revenue risk.

Transaction Details:
{transaction_details}

Customer Profile:
{customer_profile}

Risk Type: {risk_type}

Your task is to:
1. Determine the root cause category (technical, customer-side, fraud, temporary, permanent)
2. Assess the severity (low, medium, high, critical)
3. Estimate recovery probability (0-100%)
4. Recommend immediate action
5. Provide clear reasoning

Consider:
- Is this a temporary issue (insufficient funds, network error) or permanent (card cancelled)?
- Does the customer have a history of successful payments?
- What is the customer's value and tier?
- Are there patterns in the failure reason?

Respond in JSON format:
{{
    "root_cause_category": "customer-side|technical|fraud|temporary|permanent",
    "severity": "low|medium|high|critical",
    "recovery_probability": 0-100,
    "immediate_action": "retry|contact_customer|escalate|investigate",
    "reasoning": "Detailed explanation of your analysis",
    "key_factors": ["factor1", "factor2", "factor3"]
}}
"""

INTERVENTION_SELECTION_PROMPT = """You are selecting the optimal intervention strategy to recover revenue.

Risk Analysis:
{risk_diagnosis}

Customer Profile:
{customer_profile}

Available Interventions:
1. immediate_payment_retry - Retry payment immediately (best for temporary technical issues)
2. email_with_update_link - Send email with one-click card update (best for expired cards)
3. sms_reminder - Send SMS reminder (best for known customers)
4. payment_plan - Offer installment plan (best for large amounts)
5. grace_period - Extend service with reminder (best for subscriptions)

Contact History:
{contact_history}

Compliance Constraints:
- Maximum 3 contacts per week per customer
- Must honor opt-out preferences
- Must stop if customer is in dispute

Similar Past Cases:
{similar_cases}

Select the best intervention and explain why. Consider:
- What has worked for similar customers?
- What is the customer's preferred communication channel?
- Have we contacted them too recently?
- What is the urgency vs. customer relationship balance?

Respond in JSON format:
{{
    "recommended_intervention": "intervention_type",
    "strategy": "specific_strategy_name",
    "channel": "email|sms|whatsapp|voice",
    "timing": "immediate|1_hour|24_hours|3_days",
    "priority": "low|medium|high|critical",
    "reasoning": "Why this intervention is optimal",
    "expected_success_rate": 0-100,
    "alternative": "backup_intervention_if_first_fails"
}}
"""

MESSAGE_GENERATION_PROMPT = """You are crafting a personalized recovery message for a customer.

Customer Details:
- Name: {customer_name}
- Tier: {customer_tier}
- Relationship: {relationship_length}

Situation:
{situation_summary}

Intervention Type: {intervention_type}
Channel: {channel}

Guidelines:
1. Be helpful and empathetic, not pushy
2. Make it easy for them to take action
3. Match the tone to customer tier (enterprise = formal, standard = friendly)
4. Include clear call-to-action
5. Keep it concise (email: 100-150 words, SMS: 40-60 words)
6. For India market: Consider Hinglish if appropriate

{hinglish_note}

Generate:
1. Subject line (if email)
2. Message body
3. Call-to-action button text

Respond in JSON format:
{{
    "subject": "Email subject line (if applicable)",
    "body": "Message content",
    "cta": "Call-to-action text",
    "tone": "formal|friendly|casual",
    "language": "english|hinglish"
}}
"""

COMPLIANCE_CHECK_PROMPT = """You are a compliance officer reviewing a proposed intervention.

Proposed Action:
{proposed_intervention}

Customer Details:
{customer_details}

Contact History:
{contact_history}

Compliance Rules:
1. Maximum 3 contacts per week
2. No contact if customer opted out
3. Stop all contact if active dispute
4. Escalate to human for amounts > $10,000
5. Grace period required for subscriptions (3-7 days)

Check if this intervention complies with all rules.

Respond in JSON format:
{{
    "compliant": true|false,
    "violations": ["list of violated rules if any"],
    "warnings": ["list of warnings if any"],
    "required_actions": ["list of required actions before proceeding"],
    "approved": true|false,
    "reasoning": "Explanation of compliance decision"
}}
"""

EXPLANATION_PROMPT = """You are explaining an AI decision to a human user.

Decision Context:
{decision_context}

AI Reasoning:
{ai_reasoning}

Data Used:
{data_used}

Explain in simple terms:
1. What decision was made
2. Why this decision was made
3. What data points were most important
4. What alternatives were considered
5. What the expected outcome is

Use clear, non-technical language. Be transparent about uncertainty.

Respond in JSON format:
{{
    "summary": "One-sentence summary of the decision",
    "explanation": "2-3 paragraph detailed explanation",
    "key_factors": [
        {{"factor": "name", "weight": "high|medium|low", "reasoning": "why it mattered"}}
    ],
    "alternatives_considered": ["alternative1", "alternative2"],
    "confidence_level": "high|medium|low",
    "expected_outcome": "What we expect to happen"
}}
"""

# Hinglish message examples for context
HINGLISH_EXAMPLES = """
Examples of appropriate Hinglish tone for India market:

Formal: "Aapka payment pending hai. Kripya update karein."
Friendly: "Hey! Aapka card expire ho gaya hai. Ek minute mein update kar sakte ho!"
Urgent: "Aapki subscription ka payment fail ho gaya. Service interrupt na ho, abhi update karein."
"""


def format_diagnosis_prompt(
    transaction_details: dict,
    customer_profile: dict,
    risk_type: str
) -> str:
    """Format diagnosis prompt with actual data."""
    return DIAGNOSIS_PROMPT.format(
        transaction_details=format_dict(transaction_details),
        customer_profile=format_dict(customer_profile),
        risk_type=risk_type
    )


def format_intervention_prompt(
    risk_diagnosis: dict,
    customer_profile: dict,
    contact_history: dict,
    similar_cases: list
) -> str:
    """Format intervention selection prompt."""
    return INTERVENTION_SELECTION_PROMPT.format(
        risk_diagnosis=format_dict(risk_diagnosis),
        customer_profile=format_dict(customer_profile),
        contact_history=format_dict(contact_history),
        similar_cases=format_list(similar_cases)
    )


def format_message_prompt(
    customer_name: str,
    customer_tier: str,
    relationship_length: str,
    situation_summary: str,
    intervention_type: str,
    channel: str,
    use_hinglish: bool = False
) -> str:
    """Format message generation prompt."""
    hinglish_note = HINGLISH_EXAMPLES if use_hinglish else ""

    return MESSAGE_GENERATION_PROMPT.format(
        customer_name=customer_name,
        customer_tier=customer_tier,
        relationship_length=relationship_length,
        situation_summary=situation_summary,
        intervention_type=intervention_type,
        channel=channel,
        hinglish_note=hinglish_note
    )


def format_compliance_prompt(
    proposed_intervention: dict,
    customer_details: dict,
    contact_history: dict
) -> str:
    """Format compliance check prompt."""
    return COMPLIANCE_CHECK_PROMPT.format(
        proposed_intervention=format_dict(proposed_intervention),
        customer_details=format_dict(customer_details),
        contact_history=format_dict(contact_history)
    )


def format_explanation_prompt(
    decision_context: str,
    ai_reasoning: str,
    data_used: dict
) -> str:
    """Format explanation prompt."""
    return EXPLANATION_PROMPT.format(
        decision_context=decision_context,
        ai_reasoning=ai_reasoning,
        data_used=format_dict(data_used)
    )


# Helper functions
def format_dict(d: dict) -> str:
    """Format dictionary for prompt."""
    import json
    return json.dumps(d, indent=2)


def format_list(lst: list) -> str:
    """Format list for prompt."""
    import json
    return json.dumps(lst, indent=2)
