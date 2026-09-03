import uuid
from app.schemas.loan_input import LoanInput
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.empathy_agent import EmpathyAgent
from app.agents.credit_improvement_agent import CreditImprovementAgent
from app.services.agent_logger import log_agent_event
from app.db import SessionLocal
from app.models.loan_application import LoanApplication
from app.models.session import Session


class OrchestratorAgent:
    """
    Central Orchestrator for the Multi-Agent Loan Advisory System.

    Responsibilities:
    - Manage session lifecycle and database persistence
    - Invoke specialist agents (Eligibility, Credit Improvement, Empathy)
    - Enforce deterministic calculation order
    - Ensure auditability via event logging
    - Return unified financial profile & assessment response
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
        # 1. SESSION INITIALIZATION
        # -------------------------------------------------
        session_id = str(uuid.uuid4())
        db = SessionLocal()
        try:
            db_session = Session(session_id=session_id, status="active")
            db.add(db_session)
            db.commit()
        except Exception as e:
            print(f"Session init error: {e}")
            db.rollback()
        finally:
            db.close()

        # -------------------------------------------------
        # 2. ELIGIBILITY & FINANCIAL ASSESSMENT AGENT
        # -------------------------------------------------
        eligibility_result = EligibilityAgent.evaluate(loan_input)
        assessment = eligibility_result.assessment

        log_agent_event(
            session_id=session_id,
            agent_name="EligibilityAgent",
            event_type="financial_profile_assessment",
            input_snapshot=loan_input.dict(),
            output_snapshot={
                "decision": eligibility_result.decision,
                "eligibility_score": eligibility_result.eligibility_score,
                "risk_probability": eligibility_result.risk_probability,
                "dti_ratio": eligibility_result.dti_ratio,
                "reason": eligibility_result.reason,
                "assessment": assessment.dict() if assessment else None
            }
        )

        # -------------------------------------------------
        # 3. CREDIT IMPROVEMENT (IF NEEDED)
        # -------------------------------------------------
        improvement_factors = None
        personalized_advice = None

        if eligibility_result.decision in ["unlikely_eligible", "review_needed"]:
            improvement_factors = CreditImprovementAgent.get_improvement_factors(
                loan_input, eligibility_result
            )

            personalized_advice = CreditImprovementAgent.generate_personalized_advice(
                improvement_factors, loan_input, assessment
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
        # 4. EMPATHY & EXPLANATION AGENT (GEMINI LLM)
        # -------------------------------------------------
        empathy_data = EmpathyAgent.generate_response(eligibility_result)
        user_title = empathy_data.get("title", "Financial Profile Assessment")
        user_message = empathy_data.get("message", "Please review your financial assessment details.")

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
        # 5. PERSISTENCE IN DATABASE (FOR LATER PHASES)
        # -------------------------------------------------
        db = SessionLocal()
        try:
            app_id = str(uuid.uuid4())
            app_record = LoanApplication(
                application_id=app_id,
                session_id=session_id,
                monthly_income=loan_input.monthly_income,
                existing_emi=loan_input.existing_emi,
                loan_amount=loan_input.loan_amount,
                tenure_months=loan_input.tenure_months,
                employment_type=loan_input.employment_type or "salaried",
                age=loan_input.age or 30,
                credit_score=loan_input.credit_score or 750,
                loan_purpose=loan_input.loan_purpose or "personal",
                
                estimated_emi=assessment.estimated_emi if assessment else None,
                foir_percentage=assessment.projected_foir_pct if assessment else None,
                max_eligible_loan=assessment.estimated_max_loan_eligibility if assessment else None,
                dti_ratio=eligibility_result.dti_ratio,
                eligibility_score=eligibility_result.eligibility_score,
                risk_probability=eligibility_result.risk_probability,
                decision=eligibility_result.decision,
                reason=eligibility_result.reason,
                assessment_snapshot=assessment.dict() if assessment else None
            )
            db.add(app_record)
            db.commit()
        except Exception as e:
            print(f"Loan application db persistence warning: {e}")
            db.rollback()
        finally:
            db.close()

        # -------------------------------------------------
        # 6. UNIFIED USER RESPONSE
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
                "reason": eligibility_result.reason,
            },
            "assessment": assessment.dict() if assessment else None,
            "profile": {
                "monthly_income": loan_input.monthly_income,
                "existing_emi": loan_input.existing_emi,
                "loan_amount": loan_input.loan_amount,
                "tenure_months": loan_input.tenure_months,
                "employment_type": loan_input.employment_type or "salaried",
                "age": loan_input.age or 30,
                "credit_score": loan_input.credit_score or 750,
                "loan_purpose": loan_input.loan_purpose or "personal",
            }
        }

        if personalized_advice:
            response["personalized_improvement_advice"] = personalized_advice

        return response
