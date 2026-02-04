from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.core.rag_service import PolicyRAGService
from insurance_underwriter.config.config import RISK_THRESHOLDS


class RiskEvaluationEngineRAG:
    """
    RAG-powered risk evaluation engine.
    Uses policy knowledge base instead of hardcoded rules.
    """
    
    def __init__(self):
        self.rag_service = PolicyRAGService()
    
    def evaluate_risk(self, state: UnderwritingState) -> UnderwritingState:
        print(f"\n⚖️  Evaluating risk for {state['applicant_name']} using Policy RAG...")
        
        # Get relevant policy rules from RAG
        print("   🔍 Retrieving relevant policy rules...")
        policy_context = self.rag_service.get_risk_evaluation_rules(state)
        
        # Prepare applicant info for LLM
        applicant_info = {
            'age': state['age'],
            'bmi': state['bmi'],
            'smoking_status': state['smoking_status'],
            'alcohol_consumption': state['alcohol_consumption']
        }
        
        # Extract structured rules using LLM
        print("   🤖 Extracting structured rules with LLM...")
        structured_rules = self.rag_service.extract_structured_rules_with_llm(
            context=policy_context,
            applicant_info=applicant_info,
            task='risk_evaluation'
        )
        
        # Calculate risk score using extracted rules
        total_risk_score = 0
        all_flagged_conditions = []
        
        # Age-based risk
        age_risk = structured_rules.get('age_risk_score', 0)
        total_risk_score += age_risk
        if age_risk > 0:
            print(f"   Age {state['age']}: +{age_risk} points")
        
        # BMI risk
        bmi_loading = structured_rules.get('bmi_loading_factor', 1.0)
        if bmi_loading > 1.0:
            bmi_risk = int((bmi_loading - 1.0) * 50)  # Convert loading to score
            total_risk_score += bmi_risk
            all_flagged_conditions.append(f"BMI: {state['bmi']:.1f} (High BMI)")
            print(f"   BMI: +{bmi_risk} points (loading {bmi_loading}x)")
        
        # Smoking risk
        smoking_loading = structured_rules.get('smoking_loading_factor', 1.0)
        if smoking_loading > 1.0:
            smoking_risk = int((smoking_loading - 1.0) * 50)  # Convert loading to score
            total_risk_score += smoking_risk
            all_flagged_conditions.append(f"Smoking: {state['smoking_status']}")
            print(f"   Smoking: +{smoking_risk} points (loading {smoking_loading}x)")
        
        # Additional flagged conditions from LLM
        flagged_from_llm = structured_rules.get('flagged_conditions', [])
        all_flagged_conditions.extend(flagged_from_llm)
        
        # Cap at 100
        total_risk_score = min(total_risk_score, 100)
        
        # Categorize risk
        risk_category = self.categorize_risk(total_risk_score)
        
        # Update state
        state['risk_score'] = total_risk_score
        state['risk_category'] = risk_category
        state['flagged_conditions'] = all_flagged_conditions
        state['current_step'] = 'risk_evaluation_complete'
        
        print(f"✅ Risk Score: {total_risk_score:.0f}/100 ({risk_category})")
        
        return state
    
    def categorize_risk(self, risk_score: float) -> str:
        """Categorize risk based on score."""
        if risk_score >= RISK_THRESHOLDS['DECLINED']:
            return "DECLINED"
        elif risk_score >= RISK_THRESHOLDS['HIGH']:
            return "HIGH"
        elif risk_score >= RISK_THRESHOLDS['MEDIUM']:
            return "MEDIUM"
        else:
            return "LOW"
