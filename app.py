import streamlit as st
import pandas as pd

from src.pipeline import CreditRiskPipeline
from src.cache import initialize_cache

st.set_page_config(page_title="Credit Risk Engine", layout="wide")
st.title("Credit Risk Engine")
st.write("Upload applicants, assess their credit risk, and generate an AI-powered credit memo when needed.")

initialize_cache()

@st.cache_resource
def get_pipeline():
    return CreditRiskPipeline()

pipeline = get_pipeline()

required_columns = [
    "CreditUtilization",
    "Age",
    "Late30-59DaysPastDue",
    "DebtRatio",
    "MonthlyIncome",
    "OpenCreditLines",
    "Late90DaysPastDue",
    "RealEstateLoans",
    "Late60-89DaysPastDue",
    "Dependents"
]

def get_borrower(row):
    return {
        "CreditUtilization": float(row["CreditUtilization"]),
        "Age": float(row["Age"]),
        "Late30-59DaysPastDue": float(row["Late30-59DaysPastDue"]),
        "DebtRatio": float(row["DebtRatio"]),
        "MonthlyIncome": float(row["MonthlyIncome"]),
        "OpenCreditLines": float(row["OpenCreditLines"]),
        "Late90DaysPastDue": float(row["Late90DaysPastDue"]),
        "RealEstateLoans": float(row["RealEstateLoans"]),
        "Late60-89DaysPastDue": float(row["Late60-89DaysPastDue"]),
        "Dependents": float(row["Dependents"])
    }

def risk_label(risk_level):
    level = str(risk_level).strip().lower()

    if level == "high":
        return "🔴 High"
    elif level == "moderate":
        return "🟡 Moderate"
    elif level == "low":
        return "🟢 Low"

    return "⚪ Unknown"

bulk_tab, single_tab = st.tabs(["Bulk Applicants", "Single Applicant"])

# with Bulk Applicants
with bulk_tab:
    st.header("Bulk Applicants")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:

        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            missing = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing:
                st.error("Missing columns: " + ", ".join(missing))
                st.stop()

            st.success(f"{len(df)} Applicants loaded.")

            st.dataframe(df.head(), use_container_width=True)

        except Exception as e:
            st.error(f"Could not read file: {e}")
            st.stop()

        if st.button("Assess All Applicants"):

            results = []

            progress = st.progress(0)

            try:
                for i, row in df.iterrows():

                    borrower = get_borrower(row)
                    assessment = pipeline.assess(borrower)

                    context = assessment["risk_context"]
                    policy = context["policy"]

                    results.append({
                        "index": i,
                        "applicant": i + 1,
                        "probability": context["probability_of_default"],
                        "decision": context["decision"],
                        "risk_level": policy["risk_level"],
                        "action": policy["recommended_action"]
                    })

                    progress.progress(
                        (i + 1) / len(df)
                    )

                st.session_state["bulk_df"] = df
                st.session_state["bulk_results"] = results
                st.session_state["selected_memo"] = None

                st.success("All applicants assessed successfully.")

            except Exception as e:
                st.error(f"Assessment failed: {e}")

        if "bulk_results" in st.session_state:

            results = st.session_state["bulk_results"]

            st.subheader("Applicant Risk Overview")

            high = sum(
                r["risk_level"] == "High"
                for r in results
            )

            moderate = sum(
                r["risk_level"] == "Moderate"
                for r in results
            )

            low = sum(
                r["risk_level"] == "Low"
                for r in results
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("High Risk", high)
            c2.metric("Moderate Risk", moderate)
            c3.metric("Low Risk", low)

            st.divider()

            for r in results:

                row_cols = st.columns([1, 2, 2, 2, 3, 2])

                row_cols[0].write(f"#{r['applicant']}")
                row_cols[1].write(f"{r['probability']:.2f}%")
                row_cols[2].write(risk_label(r["risk_level"]))
                row_cols[3].write(r["decision"])
                row_cols[4].write(r["action"])

                if row_cols[5].button(
                    "Generate Memo",
                    key=f"memo_{r['index']}"
                ):
                    try:
                        original_row = (
                            st.session_state["bulk_df"]
                            .iloc[r["index"]]
                        )

                        borrower = get_borrower(original_row)

                        assessment = pipeline.assess(borrower)

                        memo = pipeline.generate_memo(
                            borrower,
                            assessment["risk_context"]
                        )

                        st.session_state["selected_memo"] = (
                            r["applicant"],
                            memo
                        )

                    except Exception as e:
                        st.error(f"Could not generate memo: {e}")

        if st.session_state.get("selected_memo"): 

            applicant_no, memo = st.session_state["selected_memo"]

            st.divider()

            st.subheader( f"Credit Memo — Applicant #{applicant_no}")

            st.markdown(memo)

with single_tab:

    st.header("Single Applicant Assessment")

    c1, c2 = st.columns(2)

    with c1:
        credit_utilization = st.number_input(
            "Credit Utilization",
            min_value=0.0,
            value=0.50,
            step=0.05
        )

        age = st.number_input(
            "Age",
            min_value=18.0,
            max_value=100.0,
            value=40.0,
            step=1.0
        )

        late_30_59 = st.number_input(
            "Late 30-59 Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

        debt_ratio = st.number_input(
            "Debt Ratio",
            min_value=0.0,
            value=0.50,
            step=0.05,
        )

        monthly_income = st.number_input(
            "Monthly Income",
            min_value=0.0,
            value=8000.0,
            step=500.0
        )

    with c2:
        open_credit_lines = st.number_input(
            "Open Credit Lines",
            min_value=0.0,
            value=10.0,
            step=1.0
        )

        late_90 = st.number_input(
            "Late 90+ Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

        real_estate_loans = st.number_input(
            "Real Estate Loans",
            min_value=0.0,
            value=1.0,
            step=1.0
        )

        late_60_89 = st.number_input(
            "Late 60-89 Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

        dependents = st.number_input(
            "Dependents",
            min_value=0.0,
            value=1.0,
            step=1.0
        )

    if st.button("Assess Applicant"):

        borrower = {
            "CreditUtilization": credit_utilization,
            "Age": age,
            "Late30-59DaysPastDue": late_30_59,
            "DebtRatio": debt_ratio,
            "MonthlyIncome": monthly_income,
            "OpenCreditLines": open_credit_lines,
            "Late90DaysPastDue": late_90,
            "RealEstateLoans": real_estate_loans,
            "Late60-89DaysPastDue": late_60_89,
            "Dependents": dependents
        }

        try:
            assessment = pipeline.assess(borrower)

            st.session_state["single_borrower"] = borrower
            st.session_state["single_context"] = assessment["risk_context"]

        except Exception as e:
            st.error(f"Assessment Failed: {e}")


if "single_context" in st.session_state:

    borrower = st.session_state["single_borrower"]
    context = st.session_state["single_context"]
    policy = context["policy"]

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Probability of Default",
        f"{context['probability_of_default']:.2f}%"
    )

    c2.metric(
        "Decision",
        context["decision"]
    )

    c3.metric(
        "Risk Level",
        risk_label(policy["risk_level"])
    )

    st.write(
        f"**Recommended Action:** "
        f"{policy['recommended_action']}"
    )

    if st.button("Generate Memo", key="generate_single_memo"):

        try:
            memo = pipeline.generate_memo(
                borrower,
                context
            )

            st.session_state["single_memo"] = memo

        except Exception as e:
            st.error(
                f"Could not generate memo: {e}"
            )


if "single_memo" in st.session_state:

    st.divider()

    st.subheader("AI-Generated Credit Memo")

    st.markdown(
        st.session_state["single_memo"]
    )