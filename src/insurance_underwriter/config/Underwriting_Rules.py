from typing import Dict, List, Tuple

class UnderwritingRules:

    # Chronic condition risk scores
    # CHRONIC_CONDITION_SCORES: Dict[str, int] = {
    #     'uncontrolled diabetes': 40,
    #     'diabetes': 25,
    #     'hypertension': 15,
    #     'high blood pressure': 15,
    #     'heart disease': 50,
    #     'cardiac': 50,
    #     'cancer': 60,
    #     'stroke': 55,
    #     'kidney disease': 45,
    #     'renal': 45,
    #     'copd': 35,
    #     'chronic obstructive': 35,
    #     'asthma': 10,
    #     'thyroid': 5,
    #     'liver disease': 40,
    #     'hepatic': 40
    # }
    
    # BMI risk ranges: (min, max, risk_score, category_name)
    BMI_RISK_RANGES: List[Tuple[float, float, int, str]] = [
        (0, 18.5, 10, 'underweight'),
        (18.5, 25, 0, 'normal'),
        (25, 30, 5, 'overweight'),
        (30, 40, 20, 'obese'),
        (40, 100, 35, 'morbidly_obese')
    ]
    
    # Smoking risk scores
    SMOKING_SCORES: Dict[str, int] = {
        'smoker': 30,
        'current smoker': 30,
        'former smoker': 10,
        'ex-smoker': 10,
        'non-smoker': 0,
        'never smoked': 0
    }
    
    # Alcohol consumption risk scores
    ALCOHOL_SCORES: Dict[str, int] = {
        'heavy': 20,
        'excessive': 20,
        'moderate': 5,
        'occasional': 5,
        'none': 0,
        'never': 0
    }
    
    # Age-based risk scoring
    @staticmethod
    def get_age_risk_score(age: int) -> int:
        """Calculate risk score based on age"""
        if age > 60:
            return 15
        elif age > 45:
            return 8
        elif age < 18:
            return 5
        return 0
    
    # # High-risk condition threshold for exclusions
    # EXCLUSION_THRESHOLD = 40

    # Risk Thresholds
    RISK_THRESHOLDS = {
        'DECLINED': 80,
        'HIGH': 50,
        'MEDIUM': 25,
        'LOW': 0
    }
