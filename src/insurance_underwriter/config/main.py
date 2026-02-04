from insurance_underwriter.core.document_extract_node import update_state_from_pdfs
from insurance_underwriter.config.initial_state import create_initial_state
from insurance_underwriter.core.graph import build_underwriting_workflow
from insurance_underwriter.config.config import DOCUMENTS_DIR


def print_header():
    print("\n" + "=" * 70)
    print("🏥 HEALTH INSURANCE UNDERWRITING AGENT")
    print("=" * 70)


def print_summary(state):
    print("\n" + "=" * 70)
    print("📊 UNDERWRITING DECISION SUMMARY")
    print("=" * 70)

    # Applicant Info
    print("\n👤 APPLICANT INFORMATION")
    print(f"   Name: {state['applicant_name']}")
    print(f"   Age: {state['age']} | Gender: {state['gender']}")
    print(f"   Occupation: {state['occupation']}")
    print(f"   Contact: {state['contact_number']}")
    print(f"   Email: {state['email']}")

    # Health
    print("\n⚕️  HEALTH ASSESSMENT")
    print(f"   Risk Score: {state['risk_score']:.0f}/100")
    print(f"   Risk Category: {state['risk_category']}")
    if state['bmi'] > 0:
        print(f"   BMI: {state['bmi']:.1f}")
    print(f"   Smoking: {state['smoking_status']}")
    print(f"   Alcohol: {state['alcohol_consumption']}")

    # Flags
    if state['flagged_conditions']:
        print(f"\n🚩 FLAGGED CONDITIONS ({len(state['flagged_conditions'])})")
        for i, flag in enumerate(state['flagged_conditions'], 1):
            print(f"   {i}. {flag}")

    # Premium
    print("\n💵 PREMIUM CALCULATION")
    print(f"   Base Premium: ₹{state['base_premium']:,.0f}")
    print(f"   Medical Loading: {state['medical_loading_percentage']:.0f}%")
    print(f"   Final Annual Premium: ₹{state['final_premium']:,.0f}")
    print(f"   Recommended Plan: {state['recommended_plan']}")

    # Decision
    print("\n✅ FINAL DECISION")
    print(f"   Status: {state['current_step'].upper()}")
    print(f"   Human Review Required: {'YES' if state['requires_human_review'] else 'NO'}")
    if state['requires_human_review']:
        print(f"   Review Reason: {state['review_reason']}")

    # Errors
    if state['errors']:
        print("\n⚠️  ERRORS/WARNINGS")
        for err in state['errors']:
            print(f"   - {err}")

    print("=" * 70 + "\n")


def main():
    print_header()
    
    # Create empty initial state
    state = create_initial_state()
    
    # Build workflow WITH document parsing (for CLI usage)
    print("📋 Building workflow graph...")
    workflow = build_underwriting_workflow(skip_document_parsing=False)  # ✅ Full workflow
    
    # Execute full workflow (will parse documents from DOCUMENTS_DIR)
    print("🚀 Running full underwriting workflow...\n")
    final_state = workflow.invoke(state)
    
    # Print summary
    print_summary(final_state)
    
    return final_state



if __name__ == "__main__":
    result = main()
