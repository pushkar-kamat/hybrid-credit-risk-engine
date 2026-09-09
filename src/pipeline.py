from src.risk_engine import CreditRiskEngine, build_risk_context
from src.memo_generator import CreditMemoGenerator
from src.cache import create_applicant_key, get_cached_memo, save_cached_memo


class CreditRiskPipeline:

    def __init__(self):
        self.risk_engine = CreditRiskEngine()
        self.memo_generator = CreditMemoGenerator()

    def assess(self, borrower: dict) -> dict:
        """
        Run ML prediction, SHAP explanation,
        and policy assessment.

        Does NOT call the LLM.
        """

        result = self.risk_engine.predict(borrower)
        risk_context = build_risk_context(result)

        return {
            "result": result,
            "risk_context": risk_context
        }

    def generate_memo(self, borrower: dict, risk_context: dict) -> str:
        """
        Return a cached memo when available.
        Otherwise generate it using Gemini and cache it.
        """

        try:
            applicant_key = create_applicant_key(borrower)

            # Check cache first
            cached_memo = get_cached_memo(applicant_key)

            if cached_memo is not None:
                print("Memo loaded from cache.")
                return cached_memo

            # Cache miss → call Gemini
            print("Cache miss. Generating memo with Gemini...")

            memo = self.memo_generator.generate_memo(risk_context)

            # Save generated memo
            save_cached_memo(applicant_key, memo)

            print("Memo saved to cache.")

            return memo

        except Exception as e:
            raise RuntimeError(f"Failed to generate credit memo: {e}") from e

    def run(self, borrower: dict) -> dict:
        """
        Convenience method for a single applicant.

        Performs assessment and generates a memo.
        """

        assessment = self.assess(borrower)
        memo = self.generate_memo(borrower, assessment["risk_context"])

        return {
            "result": assessment["result"],
            "risk_context": assessment["risk_context"],
            "memo": memo
        }