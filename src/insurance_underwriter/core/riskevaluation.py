from state import UnderwritingState
from insurance_underwriter.config.Underwriting_Rules import UnderwritingRules


class RiskEvaluationEngine:
    
    def __init__(self):
        self.rules = UnderwritingRules()
    
    # def evaluate_chronic_conditions(self, conditions: list) -> tuple[int, list, list]:
    #     risk_score = 0
    #     flagged = []
    #     exclusions = []
        
    #     for condition in conditions:
    #         condition_lower = condition.lower()
    #         for rule_condition, score in self.rules.CHRONIC_CONDITION_SCORES.items():
    #             if rule_condition in condition_lower:
    #                 risk_score += score
    #                 flagged.append(condition)
                    
    #                 # High-risk conditions get exclusions
    #                 if score >= self.rules.EXCLUSION_THRESHOLD:
    #                     exclusions.append(f"Exclude {condition} related claims for first 2 years")
    #                 break
        
    #     return risk_score, flagged, exclusions
    
    def evaluate_bmi(self, bmi: float) -> tuple[int, list]:
        if bmi <= 0:
            return 0, []
        
        for min_bmi, max_bmi, score, category in self.rules.BMI_RISK_RANGES:
            if min_bmi <= bmi < max_bmi:
                flagged = []
                if score > 15:  
                    flagged.append(f"BMI: {bmi:.1f} ({category})")
                return score, flagged
        
        return 0, []
    
    def evaluate_smoking(self, smoking_status: str) -> tuple[int, list]:
        status_lower = smoking_status.lower()
        
        for key, score in self.rules.SMOKING_SCORES.items():
            if key in status_lower:
                flagged = []
                if score > 0:
                    flagged.append(f"Smoking: {smoking_status}")
                return score, flagged
        
        return 0, []
    
    def evaluate_alcohol(self, alcohol_consumption: str) -> int:
        consumption_lower = alcohol_consumption.lower()
        
        for key, score in self.rules.ALCOHOL_SCORES.items():
            if key in consumption_lower:
                return score
        
        return 0
    
    def categorize_risk(self, risk_score: float) -> str:
        if risk_score >= self.rules.RISK_THRESHOLDS['DECLINED']:
            return "DECLINED"
        elif risk_score >= self.rules.RISK_THRESHOLDS['HIGH']:
            return "HIGH"
        elif risk_score >= self.rules.RISK_THRESHOLDS['MEDIUM']:
            return "MEDIUM"
        else:
            return "LOW"
    
    def evaluate_risk(self, state: UnderwritingState) -> UnderwritingState:
        """
        risk evaluation node for LangGraph

        """
        print(f"\n⚖️  Evaluating risk for {state['applicant_name']}...")
        
        total_risk_score = 0
        all_flagged_conditions = []
        all_exclusions = []
        
        # Age-based risk
        age_risk = self.rules.get_age_risk_score(state['age'])
        total_risk_score += age_risk
        print(f"   Age {state['age']}: +{age_risk} points")
        
        # # Chronic conditions
        # condition_risk, condition_flags, condition_exclusions = self.evaluate_chronic_conditions(
        #     state['chronic_conditions']
        # )
        # total_risk_score += condition_risk
        # all_flagged_conditions.extend(condition_flags)
        # all_exclusions.extend(condition_exclusions)
        # if condition_risk > 0:
        #     print(f"   Chronic conditions: +{condition_risk} points ({len(condition_flags)} flagged)")
        
        # BMI
        bmi_risk, bmi_flags = self.evaluate_bmi(state['bmi'])
        total_risk_score += bmi_risk
        all_flagged_conditions.extend(bmi_flags)
        if bmi_risk > 0:
            print(f"   BMI: +{bmi_risk} points")
        
        # Smoking
        smoking_risk, smoking_flags = self.evaluate_smoking(state['smoking_status'])
        total_risk_score += smoking_risk
        all_flagged_conditions.extend(smoking_flags)
        if smoking_risk > 0:
            print(f"   Smoking: +{smoking_risk} points")
        
        # Alcohol
        alcohol_risk = self.evaluate_alcohol(state['alcohol_consumption'])
        total_risk_score += alcohol_risk
        if alcohol_risk > 0:
            print(f"   Alcohol: +{alcohol_risk} points")
    
        
        # Cap at 100
        total_risk_score = min(total_risk_score, 100)
        
        # Categorize risk
        risk_category = self.categorize_risk(total_risk_score)
        
        # Update state
        state['risk_score'] = total_risk_score
        state['risk_category'] = risk_category
        state['flagged_conditions'] = all_flagged_conditions
        state['exclusions'] = all_exclusions
        state['current_step'] = 'risk_evaluation_complete'
        
        print(f"✅ Risk Score: {total_risk_score:.0f}/100 ({risk_category})")
        
        return state
