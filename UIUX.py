import streamlit as st
import pandas as pd
from langdetect import detect
from textblob import TextBlob

# -------------------------------
# ROUTING RULES
# -------------------------------
ROUTING_RULES = {
    "Billing": "Billing Team",
    "Technical": "Tech Team",
    "Account": "Account Team",
    "General": "Support Team"
}

# -------------------------------
# FUNCTIONS
# -------------------------------
def classify_issue(text):
    text_lower = text.lower()

    if "payment" in text_lower or "bill" in text_lower:
        return "Billing", "Payment Issue"
    elif "error" in text_lower or "crash" in text_lower:
        return "Technical", "App Error"
    elif "login" in text_lower or "account" in text_lower:
        return "Account", "Login Issue"
    else:
        return "General", "Other"


def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity < -0.2:
        sentiment = "Negative"
    elif polarity > 0.2:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    if "urgent" in text.lower() or sentiment == "Negative":
        urgency = "High"
    elif sentiment == "Neutral":
        urgency = "Medium"
    else:
        urgency = "Low"

    return sentiment, urgency


def assign_team(category):
    return ROUTING_RULES.get(category, "Support Team")


def assign_priority(urgency):
    return {"High": "P1", "Medium": "P2", "Low": "P3"}[urgency]


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="AI Ticket Classifier", layout="centered")

st.title("🎫 AI Customer Support Ticket Classifier")

# -------------------------------
# SINGLE TICKET ANALYSIS
# -------------------------------
ticket_text = st.text_area("Enter customer ticket:")

if st.button("Analyze Ticket"):
    if ticket_text.strip() == "":
        st.warning("Please enter a ticket!")
    else:
        lang = detect(ticket_text)
        category, subcategory = classify_issue(ticket_text)
        sentiment, urgency = analyze_sentiment(ticket_text)
        team = assign_team(category)
        priority = assign_priority(urgency)

        st.success("Analysis Complete")

        st.write("### Results")
        st.write(f"Language: {lang}")
        st.write(f"Category: {category}")
        st.write(f"Subcategory: {subcategory}")
        st.write(f"Sentiment: {sentiment}")
        st.write(f"Urgency: {urgency}")
        st.write(f"Team: {team}")
        st.write(f"Priority: {priority}")


# -------------------------------
# CSV UPLOAD
# -------------------------------
st.write("---")
st.write("### Batch Processing (CSV Upload)")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "ticket" not in df.columns:
        st.error("CSV must have a column named 'ticket'")
    else:
        results = []

        for _, row in df.iterrows():
            text = str(row["ticket"])

            lang = detect(text)
            category, subcategory = classify_issue(text)
            sentiment, urgency = analyze_sentiment(text)
            team = assign_team(category)
            priority = assign_priority(urgency)

            results.append({
                "ticket": text,
                "language": lang,
                "category": category,
                "subcategory": subcategory,
                "sentiment": sentiment,
                "urgency": urgency,
                "team": team,
                "priority": priority
            })

        result_df = pd.DataFrame(results)

        st.write("### Processed Results")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "output.csv", "text/csv")