from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.core.rag_service import PolicyRAGService


class PremiumCalculatorRAG:
    """
    RAG-powered premium calculator.
    Uses policy knowledge base instead of hardcoded rates.
    """
    
    def __init__(self):
        self.rag_service = PolicyRAGService()
    
    # def calculate_premium(self, state: UnderwritingState) -> UnderwritingState:
    #     print(f"\n💰 Calculating premium for {state['applicant_name']} using Policy RAG...")
        
    #     # Get relevant policy rules
    #     print("   🔍 Retrieving premium calculation rules...")
    #     policy_context = self.rag_service.get_premium_calculation_rules(state)
        
    #     # Prepare applicant info
    #     applicant_info = {
    #         'age': state['age'],
    #         'risk_category': state['risk_category'],
    #         'smoking_status': state['smoking_status'],
    #         'bmi': state['bmi']
    #     }
        
    #     # Extract structured rules using LLM
    #     print("   🤖 Extracting premium parameters with LLM...")
    #     premium_params = self.rag_service.extract_structured_rules_with_llm(
    #         context=policy_context,
    #         applicant_info=applicant_info,
    #         task='premium_calculation'
    #     )
        
    #     # Calculate premium
    #     # Since we don't have Sum Insured, we'll use a default of ₹5,00,000 (5 lakhs)
    #     sum_insured_lakhs = 5  # Default 5 lakh coverage
        
    #     base_rate_per_lakh = premium_params.get('base_rate_per_lakh', 1000)
    #     base_premium = base_rate_per_lakh * sum_insured_lakhs
        
    #     print(f"   Base premium (Age {state['age']}): ₹{base_premium:,.0f}")
        
    #     # Apply medical loading
    #     medical_loading = premium_params.get('medical_loading_percentage', 0)
    #     print(f"   Medical loading ({state['risk_category']}): {medical_loading:.0f}%")
        
    #     # Apply discount
    #     discount = premium_params.get('lifestyle_discount_percentage', 0)
    #     if discount > 0:
    #         print(f"   Lifestyle discount: -{discount:.0f}%")
        
    #     # Calculate final premium
    #     premium_with_loading = base_premium * (1 + medical_loading / 100)
    #     final_premium = premium_with_loading * (1 - discount / 100)
        
    #     print(f"   Final annual premium: ₹{final_premium:,.0f}")
        
    #     # Get recommended plan
    #     recommended_plan = premium_params.get('recommended_plan', 'STANDARD_PLAN')
        
    #     # Update state
    #     state['base_premium'] = base_premium
    #     state['medical_loading_percentage'] = medical_loading
    #     state['final_premium'] = final_premium
    #     state['recommended_plan'] = recommended_plan
    #     state['current_step'] = 'premium_calculation_complete'
        
    #     print(f"✅ Recommended plan: {recommended_plan}")
        
    #     return state
    # def calculate_premium(self, state: UnderwritingState) -> UnderwritingState:
    #     print(f"\n💰 Calculating premium for {state['applicant_name']} using Policy RAG...")
        
    #     # Get relevant policy rules
    #     print("   🔍 Retrieving premium calculation rules...")
    #     policy_context = self.rag_service.get_premium_calculation_rules(state)
        
    #     # Prepare applicant info
    #     applicant_info = {
    #         'age': state['age'],
    #         'risk_category': state['risk_category'],
    #         'smoking_status': state['smoking_status'],
    #         'bmi': state['bmi']
    #     }
        
    #     # Extract structured rules using LLM
    #     print("   🤖 Extracting premium parameters with LLM...")
    #     premium_params = self.rag_service.extract_structured_rules_with_llm(
    #         context=policy_context,
    #         applicant_info=applicant_info,
    #         task='premium_calculation'
    #     )
        
    #     # Calculate premium
    #     sum_insured_lakhs = 5  # Default 5 lakh coverage
        
    #     # Get base rate (with safety check)
    #     # Get base rate (with safety check)
    #     base_rate_per_lakh = premium_params.get('base_rate_per_lakh')

    #     # ✅ Better check: handles both None and 0
    #     if not base_rate_per_lakh:  # This catches None, 0, empty string, etc.
    #         print(f"   ⚠️  WARNING: LLM failed to extract base_rate_per_lakh from policy!")
    #         print(f"   ⚠️  premium_params received: {premium_params}")
    #         print(f"   ⚠️  This means RAG retrieval or LLM parsing failed.")
    #         raise ValueError("Failed to extract base_rate_per_lakh from policy rules. Check RAG retrieval and LLM prompt.")

    #     base_premium = base_rate_per_lakh * sum_insured_lakhs
        
    #     print(f"   Base rate per lakh: ₹{base_rate_per_lakh}")
    #     print(f"   Base premium (Age {state['age']}): ₹{base_premium:,.0f}")
        
    #     # Rest of your code...
    #     medical_loading = premium_params.get('medical_loading_percentage', 0)
    #     print(f"   Medical loading ({state['risk_category']}): {medical_loading:.0f}%")
        
    #     discount = premium_params.get('lifestyle_discount_percentage', 0)
    #     if discount > 0:
    #         print(f"   Lifestyle discount: -{discount:.0f}%")
        
    #     premium_with_loading = base_premium * (1 + medical_loading / 100)
    #     final_premium = premium_with_loading * (1 - discount / 100)
        
    #     print(f"   Final annual premium: ₹{final_premium:,.0f}")
        
    #     recommended_plan = premium_params.get('recommended_plan', 'STANDARD_PLAN')
        
    #     state['base_premium'] = base_premium
    #     state['medical_loading_percentage'] = medical_loading
    #     state['final_premium'] = final_premium
    #     state['recommended_plan'] = recommended_plan
    #     state['current_step'] = 'premium_calculation_complete'
        
    #     print(f"✅ Recommended plan: {recommended_plan}")
        
    #     return state

    def calculate_premium(self, state: UnderwritingState) -> UnderwritingState:
        from insurance_underwriter.config.config import MEDICAL_LOADINGS, PLAN_MAPPING, BASE_PREMIUMS
        
        print(f"\n💰 Calculating premium for {state['applicant_name']} using Policy RAG...")
        
        # ✅ FIX: For DECLINED cases, no premium calculation
        if state['risk_category'] == 'DECLINED':
            print("   ⚠️ Application DECLINED due to high risk score")
            print(f"   Risk Score: {state['risk_score']}/100")
            state['base_premium'] = 0
            state['medical_loading_percentage'] = 0
            state['final_premium'] = 0
            state['recommended_plan'] = PLAN_MAPPING['DECLINED']
            state['current_step'] = 'premium_calculation_complete'
            print(f"   ❌ Plan: {state['recommended_plan']}")
            return state
        
        # Get relevant policy rules for non-declined applications
        print("   🔍 Retrieving premium calculation rules...")
        policy_context = self.rag_service.get_premium_calculation_rules(state)
        
        # Prepare applicant info
        applicant_info = {
            'age': state['age'],
            'risk_category': state['risk_category'],
            'smoking_status': state['smoking_status'],
            'bmi': state['bmi']
        }
        
        # Extract structured rules using LLM
        print("   🤖 Extracting premium parameters with LLM...")
        try:
            premium_params = self.rag_service.extract_structured_rules_with_llm(
                context=policy_context,
                applicant_info=applicant_info,
                task='premium_calculation'
            )
        except Exception as e:
            print(f"   ⚠️ LLM extraction failed: {e}")
            premium_params = {}
        
        # Calculate premium
        sum_insured_lakhs = 5  # Default 5 lakh coverage
        
        # ✅ FIX: Get base rate from LLM with fallback to config.py
        base_rate_per_lakh = premium_params.get('base_rate_per_lakh')
        
        if not base_rate_per_lakh:
            print(f"   ⚠️ WARNING: LLM failed to extract base_rate_per_lakh from policy!")
            print(f"   ⚠️ Falling back to config.py BASE_PREMIUMS...")
            
            # Fallback: Use BASE_PREMIUMS from config.py
            age = state['age']
            for (min_age, max_age), annual_premium in BASE_PREMIUMS.items():
                if min_age <= age < max_age:
                    base_premium = annual_premium
                    base_rate_per_lakh = annual_premium / sum_insured_lakhs
                    print(f"   ✅ Using config.py: Age {age} → Base Premium ₹{base_premium:,.0f} (₹{base_rate_per_lakh}/lakh)")
                    break
            else:
                # If age not in range, use highest bracket
                base_premium = BASE_PREMIUMS[(60, 100)]
                base_rate_per_lakh = base_premium / sum_insured_lakhs
                print(f"   ✅ Using config.py default: ₹{base_premium:,.0f} (₹{base_rate_per_lakh}/lakh)")
        else:
            base_premium = base_rate_per_lakh * sum_insured_lakhs
            print(f"   ✅ Base rate from LLM: ₹{base_rate_per_lakh}/lakh")
        
        print(f"   Base premium (Age {state['age']}): ₹{base_premium:,.0f}")
        
        # ✅ Use config.py MEDICAL_LOADINGS (not LLM value)
        medical_loading = MEDICAL_LOADINGS[state['risk_category']]
        print(f"   Medical loading ({state['risk_category']}): {medical_loading}% (from config)")
        
        # Get lifestyle discount from LLM (can be dynamic based on health factors)
        discount = premium_params.get('lifestyle_discount_percentage', 0)
        if discount > 0:
            print(f"   Lifestyle discount: -{discount}%")
        
        # Calculate final premium
        premium_with_loading = base_premium * (1 + medical_loading / 100)
        final_premium = premium_with_loading * (1 - discount / 100)
        print(f"   Final annual premium: ₹{final_premium:,.0f}")
        
        # ✅ Use config.py PLAN_MAPPING (not LLM value)
        recommended_plan = PLAN_MAPPING[state['risk_category']]
        
        # Update state
        state['base_premium'] = base_premium
        state['medical_loading_percentage'] = medical_loading
        state['final_premium'] = final_premium
        state['recommended_plan'] = recommended_plan
        state['current_step'] = 'premium_calculation_complete'
        
        print(f"✅ Recommended plan: {recommended_plan}")
        
        return state





