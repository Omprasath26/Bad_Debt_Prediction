import requests
import streamlit as st


# PAGE CONFIG

st.set_page_config(
    page_title="Bad Debt Prediction Dashboard",
    page_icon="📊",
    layout="wide"
)


# CONFIG

API_BASE_URL = "http://127.0.0.1:8000"
HEALTH_URL = f"{API_BASE_URL}/health"
PREDICT_URL = f"{API_BASE_URL}/predict-by-customer"


# CUSTOM CSS

st.markdown("""
<style>
    .main-title {
        font-size: 34px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 16px;
        color: #4b5563;
        margin-bottom: 1.2rem;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .card {
        background-color: #ffffff;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 14px;
    }

    .metric-label {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
    }

    .status-card {
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        color: white;
        font-weight: 700;
        margin-top: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    }

    .status-good {
        background: linear-gradient(135deg, #16a34a, #22c55e);
    }

    .status-bad {
        background: linear-gradient(135deg, #ea580c, #f97316);
    }

    .status-reject {
        background: linear-gradient(135deg, #dc2626, #ef4444);
    }

    .status-title {
        font-size: 28px;
        margin-bottom: 8px;
    }

    .status-subtitle {
        font-size: 16px;
        font-weight: 500;
        opacity: 0.95;
    }

    .prediction-box {
        background-color: #f9fafb;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .footer-note {
        color: #6b7280;
        font-size: 13px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# HELPERS

def get_health_status():
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, {"detail": f"Health check failed with status code {response.status_code}"}
    except Exception as e:
        return False, {"detail": str(e)}


def fetch_prediction(customer_id: int):
    payload = {"customer_id": customer_id}
    try:
        response = requests.post(PREDICT_URL, json=payload, timeout=20)

        if response.status_code == 200:
            return True, response.json()

        try:
            error_json = response.json()
            return False, error_json
        except Exception:
            return False, {"detail": f"Request failed with status code {response.status_code}"}

    except Exception as e:
        return False, {"detail": str(e)}


def render_customer_summary(result: dict):
    snapshot = result.get("customer_snapshot", {})

    customer_id = result.get("customer_id", "N/A")
    outcome = snapshot.get("OUTCOME", "N/A")
    risk_score = snapshot.get("RISK_SCORE", "N/A")

    st.markdown('<div class="section-title">1) Customer Summary</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Customer ID</div>
            <div class="metric-value">{customer_id}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Outcome</div>
            <div class="metric-value">{outcome}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Risk Score</div>
            <div class="metric-value">{risk_score}</div>
        </div>
        """, unsafe_allow_html=True)


def render_prediction_result(result: dict):
    probability = result.get("bad_debt_probability", 0.0)
    label = result.get("prediction_label", "N/A")
    decision = result.get("decision", "N/A")
    recommendation = result.get("recommendation", "N/A")

    st.markdown('<div class="section-title">2) Prediction Result</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="prediction-box">
            <div class="metric-label">Bad Debt Probability</div>
            <div class="metric-value">{probability:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="prediction-box">
            <div class="metric-label">Prediction Label</div>
            <div class="metric-value">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="prediction-box">
            <div class="metric-label">Final Decision</div>
            <div class="metric-value">{decision}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="prediction-box">
            <div class="metric-label">Recommendation</div>
            <div class="metric-value" style="font-size:18px;">{recommendation}</div>
        </div>
        """, unsafe_allow_html=True)


def render_status_card(result: dict):
    decision = str(result.get("decision", "")).strip().lower()

    st.markdown('<div class="section-title">3) Business-Friendly Status Card</div>', unsafe_allow_html=True)

    if decision == "good":
        css_class = "status-good"
        title = "GOOD"
        subtitle = "Low repayment risk. EMI approval can be considered."
    elif decision == "bad":
        css_class = "status-bad"
        title = "BAD"
        subtitle = "Moderate repayment risk. Manual review is recommended."
    else:
        css_class = "status-reject"
        title = "REJECT"
        subtitle = "High repayment risk. EMI approval is not recommended."

    st.markdown(f"""
    <div class="status-card {css_class}">
        <div class="status-title">{title}</div>
        <div class="status-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)



# SIDEBAR - HEALTH STATUS

st.sidebar.title("System Status")

health_ok, health_data = get_health_status()

if health_ok:
    st.sidebar.success("FastAPI backend is connected")
    st.sidebar.write(f"**Model Loaded:** {health_data.get('model_loaded')}")
    st.sidebar.write(f"**Scoring Data Loaded:** {health_data.get('scoring_data_loaded')}")
    st.sidebar.write(f"**Display Data Loaded:** {health_data.get('display_data_loaded')}")
    st.sidebar.write(f"**Total Customers:** {health_data.get('total_customers_available')}")
else:
    st.sidebar.error("FastAPI backend is not reachable")
    st.sidebar.write(health_data.get("detail", "Unknown error"))


# MAIN PAGE

st.markdown('<div class="main-title">Bad Debt Prediction Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Search a customer by Customer ID and evaluate repayment risk using the deployed LightGBM model.</div>',
    unsafe_allow_html=True
)


# INPUT SECTION

with st.container():
    st.markdown('<div class="section-title">Enter Customer ID</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        customer_id_input = st.text_input(
            "Customer ID",
            placeholder="Enter customer ID here",
            label_visibility="collapsed"
        )

    with col2:
        predict_clicked = st.button("Predict", use_container_width=True)


# PREDICTION FLOW

if predict_clicked:
    if not customer_id_input.strip():
        st.warning("Please enter a Customer ID.")
    else:
        try:
            customer_id = int(customer_id_input.strip())
        except ValueError:
            st.error("Customer ID must be a valid integer.")
        else:
            with st.spinner("Fetching customer prediction from FastAPI backend..."):
                success, result = fetch_prediction(customer_id)

            if not success:
                error_msg = result.get("detail", "Prediction failed.")
                st.error(error_msg)
            else:
                render_customer_summary(result)
                render_prediction_result(result)
                render_status_card(result)

                st.markdown(
                    '<div class="footer-note">This result is generated from the deployed LightGBM Top50 production model.</div>',
                    unsafe_allow_html=True
                )

