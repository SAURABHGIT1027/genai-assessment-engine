import json
from difflib import SequenceMatcher

import pandas as pd
import streamlit as st

# Load assessment data
with open("shl_assessments.json", encoding="utf-8") as f:
    assessments_data = json.load(f)

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def recommend_assessments(query, max_results=10):
    keywords = ["python", "sql", "java", "cognitive", "personality", "communication", "reasoning", "analyst"]
    durations = {"short": 20, "medium": 40, "long": 60}

    preferred_duration = None
    for d in durations:
        if d in query.lower():
            preferred_duration = durations[d]
            break
    for num in [15, 20, 25, 30, 35, 40, 45, 50, 60]:
        if str(num) in query:
            preferred_duration = num
            break

    results = []
    for assessment in assessments_data:
        score = 0
        for kw in keywords:
            if kw in query.lower() or similar(query, kw) > 0.5:
                if kw in assessment["type"].lower() or kw in assessment["name"].lower():
                    score += 1
        if preferred_duration:
            duration_value = int(assessment["duration"].split()[0])
            if duration_value <= preferred_duration:
                score += 1
        if score > 0:
            results.append((score, assessment))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return [res[1] for res in results[:max_results]]

# Streamlit UI
st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("📊 SHL Assessment Recommendation System")
st.markdown("Enter a job description or query, and get top SHL assessments:")

query = st.text_area("✍️ Enter your job description or query")

if st.button("🔍 Recommend"):
    if query.strip():
        with st.spinner("Finding best matches..."):
            recommendations = recommend_assessments(query)

        st.success(f"✅ Top {len(recommendations)} Assessment(s) Found")

        # Display each assessment name with a clickable URL
        for a in recommendations:
            st.markdown(f"**[{a['name']}]({a['url']})**")

        # Show summary table
        df = pd.DataFrame([{
            "Assessment Name": a["name"],
            "Remote": a["remote"],
            "Adaptive": a["adaptive"],
            "Duration": a["duration"],
            "Type": a["type"]
        } for a in recommendations])

        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Please enter a job description or query.")
