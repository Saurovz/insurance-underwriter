"""
Run this script ONCE to set up the policy knowledge base.
This will create the ChromaDB database with embedded policy rules.
"""

from insurance_underwriter.core.policy_knowledge_base import setup_policy_knowledge_base

# Path to your Policy PDF
POLICY_PDF_PATH = "D:\AI_HealthCare\insurance-underwriter\src\insurance_underwriter\Policy_Doc\Health Insurance Policy Rules & Regulations 2.pdf"

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 POLICY KNOWLEDGE BASE SETUP")
    print("=" * 70)
    print("\nThis will create the ChromaDB vector database from your Policy PDF.")
    print("This only needs to be run once (or when policy PDF changes).\n")
    
    setup_policy_knowledge_base(POLICY_PDF_PATH, force_reload=False)
    
    print("\n" + "=" * 70)
    print("✅ Setup complete! You can now run your main.py")
    print("=" * 70)
