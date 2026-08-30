import uuid

from app.schemas.loan_input import LoanInput
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.empathy_agent import EmpathyAgent
from app.agents.credit_improvement_agent import CreditImprovementAgent
from app.services.agent_logger import log_agent_event


class OrchestratorAgent:
    """
    Central Orchestrator for the Multi-Agent Loan Advisory System.

    Responsibilities:
    - Manage session lifecycle
    - Invoke specialist agents
    - Enforce correct agent order
    - Ensure auditability via event logging
    - Return a unified, user-facing response
    """

    @staticmethod
    def process_loan_application(loan_input: LoanInput):
        try:
            return OrchestratorAgent._process(loan_input)
        except Exception as e:
            import traceback
            with open("error.log", "w") as f:
                f.write(traceback.format_exc())
            raise e

    @staticmethod
    def _process(loan_input: LoanInput):
        # -------------------------------------------------
        # SESSION INITIALIZATION
        # -------------------------------------------------
        session_id = str(uuid.uuid4())

        # -------------------------------------------------
        # ELIGIBILITY AGENT (RULES + ML)
        # -------------------------------------------------
        eligibility_result = EligibilityAgent.evaluate(loan_input)

        log_agent_event(
            session_id=session_id,
            agent_name="EligibilityAgent",
            event_type="eligibility_decision",
            input_snapshot=loan_input.dict(),
            output_snapshot={
                "decision": eligibility_result.decision,
                "eligibility_score": eligibility_result.eligibility_score,
                "risk_probability": eligibility_result.risk_probability,
                "dti_ratio": eligibility_result.dti_ratio,
                "reason": eligibility_result.reason
            }
        )

        # -------------------------------------------------
        # CREDIT IMPROVEMENT (ONLY IF NEEDED)
        # -------------------------------------------------
        improvement_factors = None
        personalized_advice = None

        if eligibility_result.decision in ["rejected", "conditional"]:
            improvement_factors = CreditImprovementAgent.get_improvement_factors(
                loan_input, eligibility_result
            )

            personalized_advice = CreditImprovementAgent.generate_personalized_advice(
                improvement_factors, loan_input
            )

            log_agent_event(
                session_id=session_id,
                agent_name="CreditImprovementAgent",
                event_type="personalized_credit_advice",
                input_snapshot={
                    "factors": improvement_factors
                },
                output_snapshot={
                    "advice": personalized_advice
                }
            )

        # -------------------------------------------------
        # EMPATHY / EXPLANATION AGENT (GEMINI LLM)
        # -------------------------------------------------
        empathy_data = EmpathyAgent.generate_response(eligibility_result)
        user_title = empathy_data.get("title", "Application Update")
        user_message = empathy_data.get("message", "Please review your application details.")

        log_agent_event(
            session_id=session_id,
            agent_name="EmpathyAgent",
            event_type="user_explanation",
            input_snapshot={
                "decision": eligibility_result.decision,
                "risk_probability": eligibility_result.risk_probability
            },
            output_snapshot={
                "title": user_title,
                "message": user_message
            }
        )

        # -------------------------------------------------
        # FINAL ORCHESTRATOR LOG
        # -------------------------------------------------
        log_agent_event(
            session_id=session_id,
            agent_name="OrchestratorAgent",
            event_type="final_response",
            input_snapshot=loan_input.dict(),
            output_snapshot={
                "status": eligibility_result.decision
            }
        )

        # -------------------------------------------------
        # FINAL USER RESPONSE
        # -------------------------------------------------
        response = {
            "session_id": session_id,
            "status": eligibility_result.decision,
            "title": user_title,
            "message": user_message,
            "eligibility": {
                "decision": eligibility_result.decision,
                "eligibility_score": eligibility_result.eligibility_score,
                "risk_probability": eligibility_result.risk_probability,
                "dti_ratio": eligibility_result.dti_ratio,
                "reason": eligibility_result.reason
            }
        }

        if personalized_advice:
            response["personalized_improvement_advice"] = personalized_advice

        return response
