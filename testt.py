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
# SIMPLE CLASSIFICATION
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


# -------------------------------
# SENTIMENT + URGENCY
# -------------------------------
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity < -0.2:
        sentiment = "Negative"
    elif polarity > 0.2:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    # urgency rules
    if "urgent" in text.lower() or sentiment == "Negative":
        urgency = "High"
    elif sentiment == "Neutral":
        urgency = "Medium"
    else:
        urgency = "Low"

    return sentiment, urgency


# -------------------------------
# ROUTING
# -------------------------------
def assign_team(category):
    return ROUTING_RULES.get(category, "Support Team")


def assign_priority(urgency):
    if urgency == "High":
        return "P1"
    elif urgency == "Medium":
        return "P2"
    else:
        return "P3"


# -------------------------------
# MAIN PROCESS
# -------------------------------
def process_tickets(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    results = []

    for _, row in df.iterrows():
        text = row["ticket"]

        # Language detection
        lang = detect(text)

        # Classification
        category, subcategory = classify_issue(text)

        # Sentiment & urgency
        sentiment, urgency = analyze_sentiment(text)

        # Routing
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

    pd.DataFrame(results).to_csv(output_csv, index=False)
    print("✅ Done! Output saved to", output_csv)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    process_tickets("tickets.csv", "output.csv")