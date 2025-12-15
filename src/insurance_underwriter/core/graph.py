# # Builds and compiles the LangGraph workflow
# from langgraph.graph import StateGraph, END
# from insurance_underwriter.core.Langgraph_state import UnderwritingState
# from insurance_underwriter.core.document_extract_node import update_state_from_pdfs
# from insurance_underwriter.core.risk_evaluation_node import RiskEvaluationEngine
# from insurance_underwriter.core.premium_calculation_node import PremiumCalculator
# from insurance_underwriter.core.routers import route_decision, human_review_node, final_output_node
# from insurance_underwriter.config.config import DOCUMENTS_DIR

# def parse_documents_node(state: UnderwritingState) -> UnderwritingState:
#     """Proper wrapper so LangGraph retains ALL state fields properly."""
#     return update_state_from_pdfs(state, documents_dir=DOCUMENTS_DIR)


# def build_underwriting_workflow():

#     # Initialize processors
#     risk_evaluator = RiskEvaluationEngine()
#     premium_calculator = PremiumCalculator()

#     # Create workflow
#     workflow = StateGraph(UnderwritingState)

#     # ------------- NODES -------------
#     workflow.add_node("parse_documents", parse_documents_node)
#     workflow.add_node("evaluate_risk", risk_evaluator.evaluate_risk)
#     workflow.add_node("calculate_premium", premium_calculator.calculate_premium)
#     workflow.add_node("human_review", human_review_node)
#     workflow.add_node("final_output", final_output_node)

#     # ------------- FLOW ORDER -------------
#     workflow.set_entry_point("parse_documents")
#     workflow.add_edge("parse_documents", "evaluate_risk")
#     workflow.add_edge("evaluate_risk", "calculate_premium")

#     # ------------- CONDITIONAL ROUTING -------------
#     workflow.add_conditional_edges(
#         "calculate_premium",
#         route_decision,
#         {
#             "human_review": "human_review",
#             "final_output": "final_output"
#         }
#     )

#     # ------------- TERMINATION -------------
#     workflow.add_edge("human_review", END)
#     workflow.add_edge("final_output", END)

#     return workflow.compile()



# # Builds and compiles the LangGraph workflow with RAG
# from langgraph.graph import StateGraph, END
# from insurance_underwriter.core.Langgraph_state import UnderwritingState
# from insurance_underwriter.core.document_extract_node import update_state_from_pdfs
# from insurance_underwriter.core.risk_evaluation_node_rag import RiskEvaluationEngineRAG  # NEW
# from insurance_underwriter.core.premium_calculation_node_rag import PremiumCalculatorRAG  # NEW
# from insurance_underwriter.core.routers import route_decision, human_review_node, final_output_node
# from insurance_underwriter.config.config import DOCUMENTS_DIR


# def parse_documents_node(state: UnderwritingState) -> UnderwritingState:
#     """Proper wrapper so LangGraph retains ALL state fields properly."""
#     return update_state_from_pdfs(state, documents_dir=DOCUMENTS_DIR)


# def build_underwriting_workflow():

#     # Initialize RAG-powered processors
#     risk_evaluator = RiskEvaluationEngineRAG()  # Using RAG version
#     premium_calculator = PremiumCalculatorRAG()  # Using RAG version

#     # Create workflow
#     workflow = StateGraph(UnderwritingState)

#     # ------------- NODES -------------
#     workflow.add_node("parse_documents", parse_documents_node)
#     workflow.add_node("evaluate_risk", risk_evaluator.evaluate_risk)
#     workflow.add_node("calculate_premium", premium_calculator.calculate_premium)
#     workflow.add_node("human_review", human_review_node)
#     workflow.add_node("final_output", final_output_node)

#     # ------------- FLOW ORDER -------------
#     workflow.set_entry_point("parse_documents")
#     workflow.add_edge("parse_documents", "evaluate_risk")
#     workflow.add_edge("evaluate_risk", "calculate_premium")

#     # ------------- CONDITIONAL ROUTING -------------
#     workflow.add_conditional_edges(
#         "calculate_premium",
#         route_decision,
#         {
#             "human_review": "human_review",
#             "final_output": "final_output"
#         }
#     )

#     # ------------- TERMINATION -------------
#     workflow.add_edge("human_review", END)
#     workflow.add_edge("final_output", END)

#     return workflow.compile()


# Builds and compiles the LangGraph workflow with RAG
from langgraph.graph import StateGraph, END
from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.core.document_extract_node import update_state_from_pdfs
from insurance_underwriter.core.risk_evaluation_node_rag import RiskEvaluationEngineRAG
from insurance_underwriter.core.premium_calculation_node_rag import PremiumCalculatorRAG
from insurance_underwriter.core.routers import route_decision, human_review_node, final_output_node
from insurance_underwriter.config.config import DOCUMENTS_DIR

def parse_documents_node(state: UnderwritingState) -> UnderwritingState:
    """Proper wrapper so LangGraph retains ALL state fields properly."""
    return update_state_from_pdfs(state, documents_dir=DOCUMENTS_DIR)

def build_underwriting_workflow(skip_document_parsing: bool = False):
    """
    Build underwriting workflow with optional document parsing skip.
    
    Args:
        skip_document_parsing: If True, starts from risk evaluation (for Streamlit).
                              If False, starts from document parsing (for CLI/main.py).
    """
    # Initialize RAG-powered processors
    risk_evaluator = RiskEvaluationEngineRAG()
    premium_calculator = PremiumCalculatorRAG()
    
    # Create workflow
    workflow = StateGraph(UnderwritingState)
    
    # ------------- NODES -------------
    if not skip_document_parsing:
        # Only add document parsing node if needed (for CLI)
        workflow.add_node("parse_documents", parse_documents_node)
    
    workflow.add_node("evaluate_risk", risk_evaluator.evaluate_risk)
    workflow.add_node("calculate_premium", premium_calculator.calculate_premium)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("final_output", final_output_node)
    
    # ------------- FLOW ORDER -------------
    if skip_document_parsing:
        # For Streamlit: Start directly at risk evaluation
        workflow.set_entry_point("evaluate_risk")
    else:
        # For CLI/main.py: Start with document parsing
        workflow.set_entry_point("parse_documents")
        workflow.add_edge("parse_documents", "evaluate_risk")
    
    workflow.add_edge("evaluate_risk", "calculate_premium")
    
    # ------------- CONDITIONAL ROUTING -------------
    workflow.add_conditional_edges(
        "calculate_premium",
        route_decision,
        {
            "human_review": "human_review",
            "final_output": "final_output"
        }
    )
    
    # ------------- TERMINATION -------------
    workflow.add_edge("human_review", END)
    workflow.add_edge("final_output", END)
    
    return workflow.compile()
