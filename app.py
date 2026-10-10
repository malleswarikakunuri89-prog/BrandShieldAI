
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz

st.set_page_config(
    page_title="BrandShield AI",
    page_icon="🛡️",
    layout="wide"
)

# ------------------ SAMPLE DATA ------------------

SOCIAL_DATA = [
    {
        "name": "NovaPay Official",
        "username": "@novapay_official",
        "bio": "Official NovaPay account",
        "logo_match": True
    },
    {
        "name": "NovaPay Support",
        "username": "@nova_pay_support",
        "bio": "Contact us for refunds and urgent support",
        "logo_match": True
    },
    {
        "name": "NovaPya Help",
        "username": "@novapya_help",
        "bio": "Get help with your payment account",
        "logo_match": False
    },
    {
        "name": "Sunrise Payments",
        "username": "@sunrise_payments",
        "bio": "Payment services and business solutions",
        "logo_match": False
    }
]

APP_DATA = [
    {
        "name": "NovaPay",
        "publisher": "NovaPay Technologies",
        "description": "Official NovaPay payment application",
        "logo_match": True
    },
    {
        "name": "NovaPay Rewards",
        "publisher": "Unknown Rewards Studio",
        "description": "NovaPay rewards, bonuses and special offers",
        "logo_match": True
    },
    {
        "name": "N0vaPay Wallet",
        "publisher": "Mobile Utility Labs",
        "description": "Manage your NovaPay wallet and account",
        "logo_match": False
    },
    {
        "name": "Sunrise Finance",
        "publisher": "Sunrise Software",
        "description": "Manage your personal finances",
        "logo_match": False
    }
]

SUSPICIOUS_WORDS = [
    "urgent", "refund", "free prize", "bonus",
    "verify account", "password", "claim reward"
]


# ------------------ DETECTION LOGIC ------------------

def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def similarity(brand, candidate):
    brand = normalize(brand)
    candidate = normalize(candidate)

    if not brand or not candidate:
        return 0

    return fuzz.ratio(brand, candidate)


def calculate_risk(name_score, logo_match, description,
                   publisher_mismatch=False):
    risk = 0

    if name_score >= 90:
        risk += 30
    elif name_score >= 70:
        risk += 20
    elif name_score >= 50:
        risk += 10

    if logo_match:
        risk += 25

    text = description.lower()
    if any(word in text for word in SUSPICIOUS_WORDS):
        risk += 20

    if publisher_mismatch:
        risk += 15

    return min(risk, 100)


def risk_level(score):
    if score >= 60:
        return "High"
    elif score >= 30:
        return "Medium"
    return "Low"


# ------------------ BRAND PROFILE ------------------

st.title("🛡️ BrandShield AI")
st.caption("Digital Risk Protection | Social & App Monitoring")

with st.sidebar:
    st.header("Brand Profile")

    brand = st.text_input("Company / Brand Name", "NovaPay")

    official_accounts = st.text_area(
        "Official Social Usernames",
        "@novapay_official"
    )

    official_app = st.text_input(
        "Official App Name", "NovaPay"
    )

    official_publisher = st.text_input(
        "Trusted App Publisher", "NovaPay Technologies"
    )

    st.info(
        "This demonstration uses fictional sample listings. "
        "It does not scan the live internet."
    )

official_handles = {
    item.strip().lower()
    for item in official_accounts.splitlines()
    if item.strip()
}

st.subheader("Monitoring Dashboard")

if not brand.strip():
    st.warning("Enter a brand name to begin monitoring.")
    st.stop()

# ------------------ SOCIAL MONITORING ------------------

social_results = []

for item in SOCIAL_DATA:
    username = item["username"].lower()

    # Exclude registered official usernames.
    if username in official_handles:
        continue

    score = similarity(brand, item["name"])

    risk = calculate_risk(
        score,
        item["logo_match"],
        item["bio"]
    )

    if score < 50 and not item["logo_match"]:
        continue

    social_results.append({
        "Profile": item["name"],
        "Username": item["username"],
        "Name Similarity": round(score, 1),
        "Risk Score": risk,
        "Risk Level": risk_level(risk),
        "Evidence": (
            f"Name similarity: {round(score, 1)}%; "
            f"Logo match: {item['logo_match']}; "
            f"Bio: {item['bio']}"
        )
    })

# ------------------ APP MONITORING ------------------

app_results = []

for item in APP_DATA:
    official_match = (
        normalize(item["name"]) == normalize(official_app)
        and normalize(item["publisher"])
        == normalize(official_publisher)
    )

    # Exclude the registered official app.
    if official_match:
        continue

    score = similarity(brand, item["name"])

    publisher_mismatch = (
        normalize(item["publisher"])
        != normalize(official_publisher)
    )

    risk = calculate_risk(
        score,
        item["logo_match"],
        item["description"],
        publisher_mismatch
    )

    if score < 50 and not item["logo_match"]:
        continue

    app_results.append({
        "Application": item["name"],
        "Publisher": item["publisher"],
        "Name Similarity": round(score, 1),
        "Risk Score": risk,
        "Risk Level": risk_level(risk),
        "Evidence": (
            f"Name similarity: {round(score, 1)}%; "
            f"Logo match: {item['logo_match']}; "
            f"Publisher: {item['publisher']}"
        )
    })

# ------------------ DASHBOARD ------------------

c1, c2, c3, c4 = st.columns(4)

all_results = social_results + app_results
high_risk = sum(
    result["Risk Level"] == "High"
    for result in all_results
)

c1.metric("Brand", brand)
c2.metric("Social Alerts", len(social_results))
c3.metric("App Alerts", len(app_results))
c4.metric("High-Risk Alerts", high_risk)

social_tab, app_tab, profile_tab = st.tabs([
    "Social Monitoring",
    "App Monitoring",
    "Brand Profile"
])

with social_tab:
    st.subheader("Potential Impersonation Profiles")

    if social_results:
        df = pd.DataFrame(social_results)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        selected = st.selectbox(
            "Inspect a social alert",
            df["Username"].tolist(),
            key="social_select"
        )

        row = next(
            item for item in social_results
            if item["Username"] == selected
        )

        st.write("**Evidence:**", row["Evidence"])
        st.write("**Risk score:**", row["Risk Score"], "/100")
        st.warning(
            "Potential risk only. Investigate before taking action."
        )
    else:
        st.success("No matching social profiles found.")

with app_tab:
    st.subheader("Potential Impersonation Applications")

    if app_results:
        df = pd.DataFrame(app_results)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        selected = st.selectbox(
            "Inspect an app alert",
            df["Application"].tolist(),
            key="app_select"
        )

        row = next(
            item for item in app_results
            if item["Application"] == selected
        )

        st.write("**Publisher:**", row["Publisher"])
        st.write("**Evidence:**", row["Evidence"])
        st.write("**Risk score:**", row["Risk Score"], "/100")
        st.warning(
            "A different publisher does not prove an app is malicious."
        )
    else:
        st.success("No matching apps found.")

with profile_tab:
    st.subheader("Registered Official Assets")

    st.write("**Brand:**", brand)
    st.write("**Official accounts:**")

    if official_handles:
        for handle in sorted(official_handles):
            st.write("- ", handle)
    else:
        st.write("No official accounts registered.")

    st.write("**Official app:**", official_app)
    st.write("**Trusted publisher:**", official_publisher)

st.divider()
st.subheader("Risk Overview")

if all_results:
    chart_data = pd.DataFrame([
        {"Source": "Social", "Alerts": len(social_results)},
        {"Source": "Mobile Apps", "Alerts": len(app_results)}
    ])

    fig = px.bar(
        chart_data,
        x="Source",
        y="Alerts",
        title="Potential Alerts by Source",
        color="Source"
    )

    st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Prototype demonstration only. Similarity and risk scores "
    "are heuristic signals, not probabilities of fraud."
)
