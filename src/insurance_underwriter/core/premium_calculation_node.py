from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.config.config import BASE_PREMIUMS, MEDICAL_LOADINGS, PLAN_MAPPING


class PremiumCalculator:
    
    def get_base_premium(self, age: int) -> float:

        for (min_age, max_age), premium in BASE_PREMIUMS.items():
            if min_age <= age < max_age:
                return premium
        
        # Default fallback
        return 15000
    
    def get_medical_loading(self, risk_category: str) -> float:

        return MEDICAL_LOADINGS.get(risk_category, 0)
    
    def get_recommended_plan(self, risk_category: str) -> str:

        return PLAN_MAPPING.get(risk_category, 'STANDARD_PLAN')
    
    def calculate_premium(self, state: UnderwritingState) -> UnderwritingState:

        print(f"\n💰 Calculating premium for {state['applicant_name']}...")
        
        # Get base premium
        base_premium = self.get_base_premium(state['age'])
        print(f"   Base premium (Age {state['age']}): ₹{base_premium:,.0f}")
        
        # Get medical loading
        medical_loading = self.get_medical_loading(state['risk_category'])
        print(f"   Medical loading ({state['risk_category']}): {medical_loading:.0f}%") 
        
        # Calculate final premium
        final_premium = base_premium * (1 + medical_loading / 100)
        print(f"   Final annual premium: ₹{final_premium:,.0f}")
        
        # Get recommended plan
        recommended_plan = self.get_recommended_plan(state['risk_category'])
        
        # Update state
        state['base_premium'] = base_premium
        state['medical_loading_percentage'] = medical_loading
        state['final_premium'] = final_premium
        state['recommended_plan'] = recommended_plan
        state['current_step'] = 'premium_calculation_complete'
        # state['requires_human_review'] = state.get('requires_human_review', False)
        # state['review_reason'] = state.get('review_reason', "")
        
        print(f"✅ Recommended plan: {recommended_plan}")
        
        return state
