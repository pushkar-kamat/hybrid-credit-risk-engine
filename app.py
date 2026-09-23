import pandas as pd
import streamlit as st

from src.cache import initialize_cache
from src.pipeline import CreditRiskPipeline


st.set_page_config(
    page_title="Hybrid Credit Risk Engine",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Preserve application state across theme changes.
defaults = {
    "theme": "light",
    "settings_open": False,
    "bulk_df": None,
    "bulk_results": None,
    "selected_memo": None,
    "selected_applicant": None,
    "single_borrower": None,
    "single_context": None,
    "single_memo": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


theme = st.session_state["theme"]

if theme == "dark":
    colors = {
        "background": "#0F172A",
        "surface": "#111827",
        "surface_alt": "#1E293B",
        "border": "#334155",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#60A5FA",
        "accent_hover": "#93C5FD",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "input": "#111827",
    }
else:
    colors = {
        "background": "#F6F8FB",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FAFC",
        "border": "#E2E8F0",
        "text": "#0F172A",
        "muted": "#64748B",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#DC2626",
        "input": "#FFFFFF",
    }


st.markdown(
    f"""
    <style>
        .stApp {{
            background: {colors["background"]};
            color: {colors["text"]};
        }}

        .main .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        header {{
            background: transparent !important;
        }}

        html, body, [class*="css"] {{
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        h1, h2, h3, h4 {{
            color: {colors["text"]} !important;
        }}

        p, label {{
            color: {colors["text"]};
        }}

        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1.4rem;
            border-bottom: 1px solid {colors["border"]};
            margin-bottom: 1.5rem;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 13px;
        }}

        .brand-icon {{
            width: 42px;
            height: 42px;
            border-radius: 11px;
            background: {colors["accent"]};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
        }}

        .brand-title {{
            color: {colors["text"]};
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.2;
        }}

        .brand-subtitle {{
            color: {colors["muted"]};
            font-size: 0.82rem;
            margin-top: 4px;
        }}

        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 7px 12px;
            border: 1px solid {colors["border"]};
            border-radius: 999px;
            background: {colors["surface"]};
            color: {colors["muted"]};
            font-size: 0.76rem;
            font-weight: 600;
        }}

        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: {colors["success"]};
        }}

        .section-card {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
            padding: 21px;
            margin-bottom: 18px;
        }}

        .section-title {{
            color: {colors["text"]};
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .section-description {{
            color: {colors["muted"]};
            font-size: 0.81rem;
            line-height: 1.5;
        }}

        .metric-card {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 13px;
            padding: 17px 19px;
            min-height: 100px;
        }}

        .metric-label {{
            color: {colors["muted"]};
            font-size: 0.73rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .metric-value {{
            color: {colors["text"]};
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 8px;
        }}

        .action-card {{
            background: {colors["surface_alt"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 14px 17px;
            margin: 12px 0 18px;
        }}

        .action-label {{
            color: {colors["muted"]};
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .action-value {{
            color: {colors["text"]};
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 5px;
        }}

        .memo-card {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
            padding: 24px;
            line-height: 1.7;
        }}

        .memo-header {{
            color: {colors["text"]};
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 14px;
        }}

        .risk-high,
        .risk-moderate,
        .risk-low,
        .risk-unknown {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            white-space: nowrap;
        }}

        .risk-high {{
            color: {colors["danger"]};
            background: rgba(220, 38, 38, 0.11);
            border: 1px solid rgba(220, 38, 38, 0.22);
        }}

        .risk-moderate {{
            color: {colors["warning"]};
            background: rgba(217, 119, 6, 0.11);
            border: 1px solid rgba(217, 119, 6, 0.22);
        }}

        .risk-low {{
            color: {colors["success"]};
            background: rgba(5, 150, 105, 0.11);
            border: 1px solid rgba(5, 150, 105, 0.22);
        }}

        .risk-unknown {{
            color: {colors["muted"]};
            background: rgba(100, 116, 139, 0.11);
            border: 1px solid {colors["border"]};
        }}

        .stButton > button {{
            border-radius: 9px;
            border: 1px solid {colors["border"]};
            background: {colors["surface"]};
            color: {colors["text"]};
            font-weight: 600;
            transition: 0.15s ease;
        }}

        .stButton > button:hover {{
            border-color: {colors["accent"]};
            color: {colors["accent"]};
        }}

        .stButton > button[kind="primary"] {{
            background: {colors["accent"]};
            border-color: {colors["accent"]};
            color: white;
        }}

        .stButton > button[kind="primary"]:hover {{
            background: {colors["accent_hover"]};
            border-color: {colors["accent_hover"]};
            color: white;
        }}

        div[data-baseweb="input"],
        div[data-baseweb="select"] {{
            background: {colors["input"]};
            border-radius: 9px;
        }}

        div[data-baseweb="input"] input {{
            color: {colors["text"]} !important;
        }}

        [data-testid="stFileUploader"] {{
            background: {colors["surface"]};
            border: 1px dashed {colors["border"]};
            border-radius: 12px;
            padding: 8px;
        }}

        button[data-baseweb="tab"] {{
            color: {colors["muted"]};
            font-weight: 600;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {colors["accent"]};
        }}

        hr {{
            border-color: {colors["border"]};
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            overflow: hidden;
        }}

        [data-testid="stSidebar"] {{
            background: {colors["surface"]};
            border-right: 1px solid {colors["border"]};
        }}

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: {colors["text"]} !important;
        }}

        .sidebar-label {{
            color: {colors["muted"]};
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}

        .sidebar-title {{
            color: {colors["text"]};
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 2px;
        }}

        .sidebar-description {{
            color: {colors["muted"]};
            font-size: 0.78rem;
            line-height: 1.45;
            margin-bottom: 22px;
        }}

        .sidebar-status {{
            border: 1px solid {colors["border"]};
            background: {colors["surface_alt"]};
            border-radius: 10px;
            padding: 12px;
            margin-top: 22px;
        }}

        .sidebar-status-title {{
            color: {colors["text"]};
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .sidebar-status-text {{
            color: {colors["muted"]};
            font-size: 0.72rem;
            margin-top: 3px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


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
    "Dependents",
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
        "Dependents": float(row["Dependents"]),
    }


def risk_badge(risk_level):
    level = str(risk_level).strip().lower()

    if level == "high":
        return '<span class="risk-high">HIGH RISK</span>'
    if level == "moderate":
        return '<span class="risk-moderate">MODERATE RISK</span>'
    if level == "low":
        return '<span class="risk-low">LOW RISK</span>'

    return '<span class="risk-unknown">UNKNOWN</span>'


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Sidebar settings
with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">Settings</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-description">'
        "Customize the appearance of the credit risk dashboard."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-label">Appearance</div>',
        unsafe_allow_html=True,
    )

    selected_theme = st.radio(
        "Theme",
        ["Light", "Dark"],
        index=0 if theme == "light" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )

    new_theme = selected_theme.lower()

    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        st.rerun()

    st.markdown(
        f"""
        <div class="sidebar-status">
            <div class="sidebar-status-title">
                Model Status
            </div>
            <div class="sidebar-status-text">
                ● Pipeline initialized and ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Header
header_left, header_right = st.columns([8, 2])

with header_left:
    st.markdown(
        """
        <div class="app-header">
            <div class="brand">
                <div class="brand-icon">◈</div>
                <div>
                    <div class="brand-title">
                        Hybrid Credit Risk Engine
                    </div>
                    <div class="brand-subtitle">
                        AI-assisted borrower risk assessment & credit decision support
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        """
        <div style="text-align:right; padding-top:6px;">
            <span class="status-pill">
                <span class="status-dot"></span>
                MODEL ONLINE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


bulk_tab, single_tab = st.tabs(
    ["Bulk Applicants", "Single Applicant"]
)


with bulk_tab:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                Bulk Applicant Assessment
            </div>
            <div class="section-description">
                Upload a CSV or Excel file containing multiple borrowers
                and assess them through the credit risk pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload applicant data",
        type=["csv", "xlsx"],
        help="The file must contain all required credit-risk features.",
    )

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
                st.error(
                    "Missing required columns: "
                    + ", ".join(missing)
                )
                st.stop()

            st.success(
                f"{len(df):,} applicants loaded successfully."
            )

            with st.expander("Preview uploaded data", expanded=True):
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

        except Exception as e:
            st.error(f"Could not read file: {e}")
            st.stop()

        if st.button(
            "Assess All Applicants",
            type="primary",
            use_container_width=True,
        ):
            results = []
            progress = st.progress(0)

            try:
                for i, row in df.iterrows():
                    borrower = get_borrower(row)
                    assessment = pipeline.assess(borrower)

                    context = assessment["risk_context"]
                    policy = context["policy"]

                    results.append(
                        {
                            "Applicant": i + 1,
                            "Default Probability": (
                                context["probability_of_default"]
                            ),
                            "Risk Level": policy["risk_level"],
                            "Decision": context["decision"],
                            "Recommended Action": policy[
                                "recommended_action"
                            ],
                        }
                    )

                    progress.progress((i + 1) / len(df))

                st.session_state["bulk_df"] = df
                st.session_state["bulk_results"] = results
                st.session_state["selected_memo"] = None
                st.session_state["selected_applicant"] = None

                st.success(
                    "All applicants assessed successfully."
                )

            except Exception as e:
                st.error(f"Assessment failed: {e}")

    if st.session_state["bulk_results"] is not None:
        results = st.session_state["bulk_results"]

        st.markdown("### Portfolio Risk Overview")

        high = sum(
            r["Risk Level"] == "High"
            for r in results
        )
        moderate = sum(
            r["Risk Level"] == "Moderate"
            for r in results
        )
        low = sum(
            r["Risk Level"] == "Low"
            for r in results
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "Total Applicants",
                f"{len(results):,}",
            )

        with c2:
            metric_card("High Risk", f"{high:,}")

        with c3:
            metric_card("Moderate Risk", f"{moderate:,}")

        with c4:
            metric_card("Low Risk", f"{low:,}")

        st.markdown("### Applicant Risk Overview")

        table_df = pd.DataFrame(results)

        table_df["Default Probability"] = (
            table_df["Default Probability"]
            .map(lambda value: f"{value:.2f}%")
        )

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Applicant": st.column_config.NumberColumn(
                    "Applicant",
                    width="small",
                ),
                "Default Probability": st.column_config.TextColumn(
                    "Default Probability",
                    width="medium",
                ),
                "Risk Level": st.column_config.TextColumn(
                    "Risk Level",
                    width="medium",
                ),
                "Decision": st.column_config.TextColumn(
                    "Decision",
                    width="medium",
                ),
                "Recommended Action": st.column_config.TextColumn(
                    "Recommended Action",
                    width="large",
                ),
            },
        )

        st.markdown("### Credit Memo")

        applicant_numbers = [
            r["Applicant"]
            for r in results
        ]

        selected_applicant = st.selectbox(
            "Select an applicant",
            applicant_numbers,
            index=(
                applicant_numbers.index(
                    st.session_state["selected_applicant"]
                )
                if st.session_state["selected_applicant"]
                in applicant_numbers
                else 0
            ),
        )

        st.session_state["selected_applicant"] = (
            selected_applicant
        )

        if st.button(
            "Generate Credit Memo",
            type="primary",
            use_container_width=True,
            key="bulk_generate_memo",
        ):
            try:
                result = next(
                    r for r in results
                    if r["Applicant"] == selected_applicant
                )

                original_row = (
                    st.session_state["bulk_df"]
                    .iloc[result["Applicant"] - 1]
                )

                borrower = get_borrower(original_row)
                assessment = pipeline.assess(borrower)

                memo = pipeline.generate_memo(
                    borrower,
                    assessment["risk_context"],
                )

                st.session_state["selected_memo"] = (
                    selected_applicant,
                    memo,
                )

            except Exception as e:
                st.error(
                    f"Could not generate memo: {e}"
                )

    if st.session_state["selected_memo"] is not None:
        applicant_no, memo = st.session_state[
            "selected_memo"
        ]

        st.markdown("### AI Credit Memo")

        st.markdown(
            f"""
            <div class="memo-card">
                <div class="memo-header">
                    Credit Memo — Applicant #{applicant_no}
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(memo)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


with single_tab:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                Single Applicant Assessment
            </div>
            <div class="section-description">
                Enter borrower financial information to generate
                an individual credit risk assessment.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Borrower Financial Profile")

    c1, c2 = st.columns(2)

    with c1:
        credit_utilization = st.number_input(
            "Credit Utilization",
            min_value=0.0,
            value=0.50,
            step=0.05,
            help="Ratio of revolving credit currently being used.",
        )

        age = st.number_input(
            "Age",
            min_value=18.0,
            max_value=100.0,
            value=40.0,
            step=1.0,
        )

        late_30_59 = st.number_input(
            "Late 30–59 Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0,
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
            step=500.0,
        )

    with c2:
        open_credit_lines = st.number_input(
            "Open Credit Lines",
            min_value=0.0,
            value=10.0,
            step=1.0,
        )

        late_90 = st.number_input(
            "Late 90+ Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        real_estate_loans = st.number_input(
            "Real Estate Loans",
            min_value=0.0,
            value=1.0,
            step=1.0,
        )

        late_60_89 = st.number_input(
            "Late 60–89 Days Past Due",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        dependents = st.number_input(
            "Dependents",
            min_value=0.0,
            value=1.0,
            step=1.0,
        )

    if st.button(
        "Assess Credit Risk",
        type="primary",
        use_container_width=True,
    ):
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
            "Dependents": dependents,
        }

        try:
            assessment = pipeline.assess(borrower)

            st.session_state["single_borrower"] = borrower
            st.session_state["single_context"] = (
                assessment["risk_context"]
            )
            st.session_state["single_memo"] = None

        except Exception as e:
            st.error(f"Assessment failed: {e}")

    if st.session_state["single_context"] is not None:
        borrower = st.session_state["single_borrower"]
        context = st.session_state["single_context"]
        policy = context["policy"]

        st.markdown("### Risk Assessment")

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Probability of Default",
                f"{context['probability_of_default']:.2f}%",
            )

        with c2:
            metric_card(
                "Decision",
                context["decision"],
            )

        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Risk Level</div>
                    <div style="margin-top:12px;">
                        {risk_badge(policy["risk_level"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="action-card">
                <div class="action-label">
                    Recommended Action
                </div>
                <div class="action-value">
                    {policy["recommended_action"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Generate AI Credit Memo",
            type="primary",
            use_container_width=True,
            key="generate_single_memo",
        ):
            try:
                memo = pipeline.generate_memo(
                    borrower,
                    context,
                )

                st.session_state["single_memo"] = memo

            except Exception as e:
                st.error(
                    f"Could not generate memo: {e}"
                )

    if st.session_state["single_memo"] is not None:
        st.markdown("### AI Credit Memo")

        st.markdown(
            """
            <div class="memo-card">
                <div class="memo-header">
                    AI-Generated Credit Assessment
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            st.session_state["single_memo"]
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


st.markdown(
    f"""
    <div style="
        text-align:center;
        color:{colors["muted"]};
        font-size:0.72rem;
        padding-top:35px;
    ">
        Hybrid Credit Risk Engine · AI-assisted decision support
    </div>
    """,
    unsafe_allow_html=True,
)