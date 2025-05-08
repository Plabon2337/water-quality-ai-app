import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page setup with visual improvements
st.set_page_config(page_title="Water Quality AI Tool", page_icon="🌊", layout="centered")
st.image("https://cdn-icons-png.flaticon.com/512/4273/4273786.png", width=100)
st.title("💧 Water Quality Indexing & AI-Based Analysis Tool")
st.markdown("""
Select the **type of water source** and enter relevant test data (you can leave any field blank).
The app will provide regulatory comparisons, analysis, and treatment recommendations.
""")

# New: Input for source location (optional)
sample_location = st.text_input("Optional: Enter Sample Source & Location")

water_type = st.selectbox("Select Type of Water", [
    "River Water", "Lake Water", "Sea Water", "Aquifer Groundwater", "Natural Spring", "Source Unspecified Water"
])

# WHO and ECR'2023 guideline values (with units)
guidelines = {
    'BOD5 (mg/L)': {'WHO': 6, 'ECR': 6},
    'COD (mg/L)': {'WHO': 10, 'ECR': 4},
    'pH (-)': {'WHO': (6.5, 8.5), 'ECR': (6.5, 8.5)},
    'Temperature (°C)': {'WHO': 25, 'ECR': 30},
    'Turbidity (NTU)': {'WHO': 5, 'ECR': 10},
    'Color-465nm (Pt-Co unit)': {'WHO': 15, 'ECR': 15},
    'TSS (mg/L)': {'WHO': 10, 'ECR': 10},
    'TIN (mg/L)': {'WHO': 1, 'ECR': 1},
    'Free ammonia (mg/L)': {'WHO': 0.5, 'ECR': 0.5},
    'Chromium (mg/L)': {'WHO': 0.05, 'ECR': 0.05},
    'Cobalt (mg/L)': {'WHO': 0.01, 'ECR': 0.01}
}

st.markdown("---")
st.markdown("### 🔬 Enter Sample Data Below")

data = {}
for test in guidelines.keys():
    col1, col2, col3 = st.columns(3)
    with col1:
        val1 = st.text_input(f"{test} - Sample 1", key=f"{test}_1")
    with col2:
        val2 = st.text_input(f"{test} - Sample 2", key=f"{test}_2")
    with col3:
        val3 = st.text_input(f"{test} - Sample 3", key=f"{test}_3")
    data[test] = [val1, val2, val3]

if st.button("🚀 Analyze Water Quality"):
    collected_data = {}
    for test, samples in data.items():
        try:
            values = [float(v) for v in samples if v.strip() != '']
            if values:
                collected_data[test] = values
        except ValueError:
            st.error(f"Invalid input in {test}. Please enter numbers only.")
            st.stop()

    st.balloons()
    st.subheader("📊 1. Comparison with ECR'2023 and WHO Guidelines")
    comparison_rows = []
    for test, values in collected_data.items():
        avg_value = sum(values) / len(values)
        who_limit = guidelines[test]['WHO']
        ecr_limit = guidelines[test]['ECR']

        if isinstance(who_limit, tuple):
            who_status = "OK" if who_limit[0] <= avg_value <= who_limit[1] else "Exceeds"
            ecr_status = "OK" if ecr_limit[0] <= avg_value <= ecr_limit[1] else "Exceeds"
        else:
            who_status = "OK" if avg_value <= who_limit else "Exceeds"
            ecr_status = "OK" if avg_value <= ecr_limit else "Exceeds"

        comparison_rows.append({
            'Parameter': test,
            'Avg Value': avg_value,
            'WHO Limit': who_limit,
            'WHO Status': who_status,
            'ECR Limit': ecr_limit,
            'ECR Status': ecr_status
        })

    df = pd.DataFrame(comparison_rows)
    st.dataframe(df)

    st.subheader("🧠 2. AI-Based Analysis Report")
    st.subheader("🧪 3. Suggested Water Treatment Process")

    prompt = f"""
You are an expert environmental engineer. Based on the following water test results from a {water_type}, write a concise report with:
1. An analysis of the water condition (suitability for drinking, irrigation, health/environment risks).
2. Recommend a simple treatment process suitable for this water to become potable or recreational.

Location: {sample_location or 'Not provided'}
Test results:
{collected_data}

Compare the results with WHO and ECR 2023 guidelines.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a water quality expert."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_text = response.choices[0].message.content
        st.markdown(ai_text)
    except Exception as e:
        st.error(f"OpenAI API error: {e}")