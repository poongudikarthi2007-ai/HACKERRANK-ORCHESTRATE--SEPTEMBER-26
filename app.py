import streamlit as st
import pandas as pd
from pathlib import Path

from data_loader import load_data
from llm_agent import make_decision


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Afforda | Smart Purchase Advisor",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS — dark, card-driven theme
# =========================================================

st.markdown(
    """
    <style>
        /* ---- Global ---- */
        .stApp {
            background: linear-gradient(180deg, #0f1220 0%, #14172a 100%);
        }

        /* ---- Hero header ---- */
        .hero {
            background: linear-gradient(120deg, #6C5CE7 0%, #00B8D9 100%);
            padding: 34px 40px;
            border-radius: 18px;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px rgba(108, 92, 231, 0.25);
        }
        .hero h1 {
            color: white;
            font-size: 36px;
            font-weight: 800;
            margin: 0;
        }
        .hero p {
            color: rgba(255,255,255,0.85);
            font-size: 16px;
            margin-top: 6px;
        }

        /* ---- Section labels ---- */
        .section-label {
            color: #A29BFE;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        /* ---- Card ---- */
        .card {
            background: #1B1E33;
            border: 1px solid #2A2E4A;
            border-radius: 14px;
            padding: 20px 22px;
            margin-bottom: 16px;
        }

        /* ---- Pill badges for status ---- */
        .pill {
            display: inline-block;
            padding: 10px 22px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.4px;
        }
        .pill-green   { background: #123524; color: #4ADE80; border: 1px solid #1F5C3B; }
        .pill-yellow  { background: #3A2E12; color: #FACC15; border: 1px solid #5C4B1F; }
        .pill-blue    { background: #12283A; color: #38BDF8; border: 1px solid #1F4B5C; }
        .pill-red     { background: #3A1414; color: #F87171; border: 1px solid #5C1F1F; }
        .pill-gray    { background: #2A2A2A; color: #D1D5DB; border: 1px solid #444444; }

        /* ---- Stat tile ---- */
        .stat-tile {
            background: #1B1E33;
            border: 1px solid #2A2E4A;
            border-radius: 14px;
            padding: 16px 18px;
            text-align: center;
        }
        .stat-tile .label {
            color: #8B90B3;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .stat-tile .value {
            color: #EDEDF7;
            font-size: 22px;
            font-weight: 700;
        }

        /* ---- Text tweaks ---- */
        h1, h2, h3, h4, p, span, div, label {
            color: #EDEDF7;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1B1E33;
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧭 Afforda — Smart Purchase Advisor</h1>
        <p>An AI Agent that tells you whether to buy now, spread the cost, or wait.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_project_data():

    return load_data()


try:

    (
        requests,
        sample_requests,
        profiles,
        events,
        exchange_rates,
        payment_options,
        messages,
        images
    ) = load_project_data()

except Exception as e:

    st.error("Unable to load project data.")
    st.exception(e)
    st.stop()


# =========================================================
# SIDEBAR — request picker + quick profile glance
# =========================================================

with st.sidebar:

    st.markdown("### 🔎 Choose a Request")

    request_ids = requests["request_id"].tolist()

    selected_request_id = st.selectbox(
        "Request ID",
        request_ids,
        label_visibility="collapsed"
    )

    selected_request = requests[
        requests["request_id"] == selected_request_id
    ].iloc[0]

    user_id = selected_request["user_id"]

    user_profile = profiles[
        profiles["user_id"] == user_id
    ]

    if user_profile.empty:
        st.error(f"No financial profile found for user: {user_id}")
        st.stop()

    profile = user_profile.iloc[0]

    user_events = events[
        events["user_id"] == user_id
    ].copy()

    st.markdown("---")
    st.markdown("### 👤 User Snapshot")
    st.write(f"**User:** {user_id}")
    st.write(f"**Home currency:** {profile['home_currency']}")
    st.write(
        f"**Balance:** "
        f"{float(profile['current_available_balance']):,.2f} "
        f"{profile['home_currency']}"
    )
    st.write(
        f"**Min. balance to keep:** "
        f"{float(profile['minimum_balance_to_keep']):,.2f}"
    )

    st.markdown("---")
    run_analysis = st.button(
        "🚀 Run AI Analysis",
        type="primary",
        use_container_width=True
    )


# =========================================================
# TOP STAT STRIP
# =========================================================

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(
        f"""<div class="stat-tile">
                <div class="label">Request ID</div>
                <div class="value">{selected_request['request_id']}</div>
            </div>""",
        unsafe_allow_html=True
    )

with s2:
    st.markdown(
        f"""<div class="stat-tile">
                <div class="label">User</div>
                <div class="value">{selected_request['user_id']}</div>
            </div>""",
        unsafe_allow_html=True
    )

with s3:
    st.markdown(
        f"""<div class="stat-tile">
                <div class="label">Requested Amount</div>
                <div class="value">{selected_request['requested_amount']:,.2f}</div>
            </div>""",
        unsafe_allow_html=True
    )

with s4:
    st.markdown(
        f"""<div class="stat-tile">
                <div class="label">Currency</div>
                <div class="value">{profile['home_currency']}</div>
            </div>""",
        unsafe_allow_html=True
    )

st.write("")


# =========================================================
# TABS — Overview | Financial Profile | History
# =========================================================

tab_overview, tab_profile, tab_history = st.tabs(
    ["📋 Overview", "💳 Financial Profile", "📅 History"]
)


# ---- OVERVIEW TAB -----------------------------------------------------
with tab_overview:

    st.markdown('<div class="section-label">Request Details</div>', unsafe_allow_html=True)

    request_data = {
        "Request ID": selected_request["request_id"],
        "User ID": selected_request["user_id"],
        "Amount": selected_request["requested_amount"],
        "Request Date": selected_request["request_date"],
        "Desired Completion Date": selected_request["desired_completion_date"]
    }

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame(request_data.items(), columns=["Field", "Value"]),
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ---- FINANCIAL PROFILE TAB --------------------------------------------
with tab_profile:

    st.markdown('<div class="section-label">Balances</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Available Balance</div>
                    <div class="value">{float(profile['current_available_balance']):,.2f}</div>
                </div>""",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Minimum Balance</div>
                    <div class="value">{float(profile['minimum_balance_to_keep']):,.2f}</div>
                </div>""",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Currency</div>
                    <div class="value">{profile['home_currency']}</div>
                </div>""",
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Max Installments</div>
                    <div class="value">{profile['max_installment_months']}</div>
                </div>""",
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown('<div class="section-label">Preferences</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)

    with pc1:
        st.write("**🎯 Financial Priorities**")
        st.write(profile["financial_priorities"])

        st.write("**🛡️ Protected Expenses**")
        st.write(profile["expense_categories_to_protect"])

    with pc2:
        st.write("**✂️ Willing to Reduce**")
        st.write(profile["expense_categories_user_is_willing_to_reduce"])

        st.write("**🚫 Willing to Stop**")
        st.write(profile["expense_categories_user_is_willing_to_stop"])

    st.write("**💳 Accepted Payment Methods**")
    st.write(profile["payment_methods_user_will_consider"])

    st.markdown('</div>', unsafe_allow_html=True)


# ---- HISTORY TAB --------------------------------------------------------
with tab_history:

    st.markdown('<div class="section-label">Financial Events</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if user_events.empty:
        st.info("No financial events found.")
    else:
        st.dataframe(
            user_events,
            use_container_width=True,
            hide_index=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# RUN DECISION
# =========================================================

if run_analysis:

    with st.spinner("Analyzing financial situation..."):

        try:

            # llm_agent.make_decision expects an "amount" field, but the
            # requests table stores it as "requested_amount" — alias it
            # here so we don't have to touch llm_agent.py.
            request_for_agent = selected_request.copy()
            request_for_agent["amount"] = request_for_agent["requested_amount"]

            decision = make_decision(
                request_for_agent,
                profile,
                user_events,
                payment_options
            )

            st.session_state["decision"] = decision

        except Exception as e:

            st.error("Error while generating the decision.")
            st.exception(e)


# =========================================================
# DECISION RESULT
# =========================================================

if "decision" in st.session_state:

    decision = st.session_state["decision"]

    st.write("")
    st.markdown("## 📊 AI Decision")

    status = decision.get("affordability_status", "unknown")

    status_map = {
        "affordable_now":        ("pill-green",  "✅ AFFORDABLE NOW"),
        "affordable_with_plan":  ("pill-yellow", "⚠️ AFFORDABLE WITH PAYMENT PLAN"),
        "affordable_later":      ("pill-blue",   "🕒 WAIT UNTIL A LATER DATE"),
        "not_affordable":        ("pill-red",    "❌ NOT AFFORDABLE"),
    }

    pill_class, pill_label = status_map.get(status, ("pill-gray", f"Decision: {status}"))

    st.markdown(
        f'<span class="pill {pill_class}">{pill_label}</span>',
        unsafe_allow_html=True
    )

    st.write("")

    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Safe Amount</div>
                    <div class="value">{decision.get('amount_safe_to_pay', 0):,.2f}</div>
                </div>""",
            unsafe_allow_html=True
        )

    with d2:
        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Payment Method</div>
                    <div class="value">{decision.get('recommended_payment_method', 'N/A')}</div>
                </div>""",
            unsafe_allow_html=True
        )

    with d3:
        earliest_date = decision.get("earliest_date_for_full_payment")
        earliest_display = str(earliest_date) if earliest_date else "Not available"

        st.markdown(
            f"""<div class="stat-tile">
                    <div class="label">Earliest Full Payment</div>
                    <div class="value">{earliest_display}</div>
                </div>""",
            unsafe_allow_html=True
        )

    st.write("")

    detail_tab1, detail_tab2, detail_tab3 = st.tabs(
        ["💳 Payment Plan", "📉 Spending Changes", "🧠 Explanation"]
    )

    with detail_tab1:
        payment_plan = decision.get("payment_plan", "none")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        if isinstance(payment_plan, dict):
            st.json(payment_plan)
        else:
            st.write(str(payment_plan))
        st.markdown('</div>', unsafe_allow_html=True)

    with detail_tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(
            decision.get(
                "spending_changes_needed",
                "No spending changes specified."
            )
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with detail_tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(
            decision.get(
                "decision_explanation",
                "No explanation available."
            )
        )
        st.markdown('</div>', unsafe_allow_html=True)

else:

    st.info("👈 Use **Run AI Analysis** in the sidebar to generate a decision for this request.")


# =========================================================
# FOOTER
# =========================================================

st.write("")
st.markdown(
    "<hr style='border-color:#2A2E4A;'>"
    "<p style='text-align:center; color:#8B90B3; font-size:13px;'>"
    "Afforda | AI-powered financial planning system"
    "</p>",
    unsafe_allow_html=True
)