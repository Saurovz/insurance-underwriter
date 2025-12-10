from typing import Literal
from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.config.config import HUMAN_REVIEW_CONFIG

def route_decision(state: UnderwritingState) -> Literal["human_review", "final_output"]:

    
    # Check 1: High risk categories always need review
    if state['risk_category'] in HUMAN_REVIEW_CONFIG['high_risk_categories']:
        state['requires_human_review'] = True
        state['review_reason'] = f"High risk category: {state['risk_category']}"
        return "human_review"
    
    # Check 2: Too many flagged conditions
    if len(state['flagged_conditions']) > HUMAN_REVIEW_CONFIG['max_auto_flagged_conditions']:
        state['requires_human_review'] = True
        state['review_reason'] = f"Multiple flagged conditions: {len(state['flagged_conditions'])}"
        return "human_review"
    
    # Check 3: Medium risk with elevated score
    if (state['risk_category'].upper() == 'MEDIUM' and 
        state['risk_score'] > HUMAN_REVIEW_CONFIG['medium_risk_score_threshold']):
        state['requires_human_review'] = True
        state['review_reason'] = f"Medium risk with elevated score: {state['risk_score']:.0f}"
        return "human_review"
    
    # Check 4: Any policy exclusions require review
    if len(state['exclusions']) > 0:
        state['requires_human_review'] = True
        state['review_reason'] = f"Policy exclusions required: {len(state['exclusions'])}"
        return "human_review"
    
    # All checks passed - auto-approve
    state['requires_human_review'] = False
    
    return "final_output"


def human_review_node(state: UnderwritingState) -> UnderwritingState:

    print(f"\n👤 ROUTING TO HUMAN UNDERWRITER")
    print(f"   Reason: {state['review_reason']}")
    print(f"   Risk: {state['risk_category']} ({state['risk_score']:.0f}/100)")
    print(f"   Flagged: {len(state['flagged_conditions'])} conditions")
    print("DEBUG ROUTER BEFORE RETURN:", state['requires_human_review'], state['review_reason'])

    state['current_step'] = 'pending_human_review'
    return state


def final_output_node(state: UnderwritingState) -> UnderwritingState:

    print(f"\n✅ AUTO-APPROVED")
    print(f"   Applicant: {state['applicant_name']}")
    print(f"   Plan: {state['recommended_plan']}")
    print(f"   Premium: ₹{state['final_premium']:,.0f}/year")
    
    state['current_step'] = 'completed'
    return state

