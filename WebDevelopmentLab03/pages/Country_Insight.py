import streamlit as st
import requests
import google.generativeai as genai

# ---------- Page config ----------
st.set_page_config(
    page_title="Country Insight",
    page_icon="🌍",
    layout="wide"
)

# ---------- HEADER CONTAINER ----------
with st.container():
    st.title("🌍 Country Insight (Phase 3)")
    st.write(
        "Generate AI-powered insights about countries using live data from the REST Countries API "
        "and Google Gemini. This page focuses on structured summaries and comparisons."
    )

# ---------- Configure Gemini ----------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # IMPORTANT:
    # Use the SAME model name here that works in your chatbot page.
    # If your chatbot works with "gemini-1.5-flash", use that instead.
    INSIGHT_MODEL_NAME = "gemini-flash-latest"
    insight_model = genai.GenerativeModel(INSIGHT_MODEL_NAME)

    GEMINI_READY = True
except Exception as e:
    GEMINI_READY = False
    st.error("⚠️ Gemini is not configured correctly for Country Insight.")
    st.error(f"Debug info (Gemini config): {e}")

# ---------- REST Countries Helper ----------
BASE_URL = "https://restcountries.com/v3.1"

def get_country_data(name: str):
    """Fetch structured data for a single country."""
    if not name:
        return None

    try:
        resp = requests.get(f"{BASE_URL}/name/{name}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                c = data[0]
                return {
                    "name": c.get("name", {}).get("common"),
                    "official_name": c.get("name", {}).get("official"),
                    "capital": c.get("capital", ["Unknown"])[0],
                    "region": c.get("region", "Unknown"),
                    "subregion": c.get("subregion", "Unknown"),
                    "population": c.get("population", 0),
                    "area": c.get("area", 0),
                    "languages": list((c.get("languages") or {}).values()),
                    "currencies": list((c.get("currencies") or {}).keys()),
                    "flag": c.get("flag", ""),
                }
    except Exception:
        return None

    return None

def format_country_block(c: dict) -> str:
    """Format a single country's data as text for the LLM."""
    if not c:
        return "No data available."

    return (
        f"Name: {c.get('name')} (official: {c.get('official_name')})\n"
        f"Capital: {c.get('capital')}\n"
        f"Region: {c.get('region')} | Subregion: {c.get('subregion')}\n"
        f"Population: {c.get('population'):,}\n"
        f"Area: {c.get('area'):,} km²\n"
        f"Languages: {', '.join(c.get('languages', [])) or 'Unknown'}\n"
        f"Currencies: {', '.join(c.get('currencies', [])) or 'Unknown'}\n"
        f"Flag: {c.get('flag')}\n"
    )

# ---------- Gemini Wrapper ----------
def generate_country_insight(primary_data, secondary_data, insight_type, detail_level, extra_note):
    """Call Gemini to generate a structured insight based on country data."""
    if not GEMINI_READY:
        return "Gemini is not available right now. Please check the API key configuration."

    system_instructions = (
        "You are an assistant that analyzes REST Countries API data. "
        "You must base concrete facts (like population, capital, region, area) on the provided data. "
        "If something is not in the data, say you are not sure instead of guessing. "
        "Write clearly, in paragraphs, and stay friendly and informative."
    )

    primary_block = format_country_block(primary_data)
    secondary_block = format_country_block(secondary_data) if secondary_data else "No comparison country provided."

    detail_text = {
        1: "very short, 2–3 sentence overview",
        2: "medium-length explanation, around one short paragraph",
        3: "more detailed, 2–3 short paragraphs with key facts and commentary",
    }[detail_level]

    prompt = f"""
{system_instructions}

Insight type requested: {insight_type}
Desired detail level: {detail_text}

Primary country data:
{primary_block}

Comparison country data:
{secondary_block}

Additional user note or focus:
{extra_note or "None."}

Now write the requested insight in a way that would make sense to a student exploring these countries.
"""

    try:
        response = insight_model.generate_content(prompt)
        if not hasattr(response, "text") or response.text is None:
            return "I couldn't generate an insight. Try changing your inputs or trying again."
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API error (Country Insight): {e}")
        return "Sorry, something went wrong while generating the insight. Please try again."

# ---------- Sidebar Inputs (Phase 3 requirements) ----------
st.sidebar.header("Country Insight Settings")

primary_country = st.sidebar.text_input(
    "Primary country",
    value="France",
    help="This is the main country the insight will focus on."
)

compare_mode = st.sidebar.checkbox(
    "Add a comparison country?",
    value=False
)

secondary_country = None
if compare_mode:
    secondary_country = st.sidebar.text_input(
        "Comparison country",
        value="Germany",
        help="Optional: compare the primary country with this one."
    )

insight_type = st.sidebar.selectbox(
    "Type of insight",
    [
        "Travel-style overview",
        "Economic & demographic snapshot",
        "Culture, language, and region context",
        "Why this country is interesting to visit or study",
    ]
)

detail_level = st.sidebar.slider(
    "Detail level",
    min_value=1,
    max_value=3,
    value=2,
    format="%d",
    help="1 = very short, 3 = more detailed"
)

extra_note = st.sidebar.text_area(
    "Optional focus or question",
    placeholder="Example: Focus on safety and tourism. Or: Compare population density.",
    height=80
)

# ---------- Fetch data once so we can reuse it ----------
primary_data = get_country_data(primary_country)
secondary_data = None
if compare_mode and secondary_country:
    secondary_data = get_country_data(secondary_country)

# ---------- MAIN LAYOUT USING TABS + CONTAINERS ----------
data_tab, insight_tab = st.tabs(["📊 Data View", "🧾 AI Insight"])

# ----- TAB 1: DATA VIEW -----
with data_tab:
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Primary Country Data")
            if primary_data:
                st.write(f"**{primary_data['name']}** {primary_data.get('flag', '')}")
                st.write(f"**Capital:** {primary_data['capital']}")
                st.write(f"**Region:** {primary_data['region']} — {primary_data['subregion']}")
                st.write(f"**Population:** {primary_data['population']:,}")
                st.write(f"**Area:** {primary_data['area']:,} km²")
                st.write(f"**Languages:** {', '.join(primary_data['languages']) or 'Unknown'}")
                st.write(f"**Currencies:** {', '.join(primary_data['currencies']) or 'Unknown'}")
            else:
                st.warning(f"Could not load data for '{primary_country}'. Please check the spelling.")

        with col2:
            st.subheader("📎 Comparison Country Data")
            if compare_mode and secondary_country:
                if secondary_data:
                    st.write(f"**{secondary_data['name']}** {secondary_data.get('flag', '')}")
                    st.write(f"**Capital:** {secondary_data['capital']}")
                    st.write(f"**Region:** {secondary_data['region']} — {secondary_data['subregion']}")
                    st.write(f"**Population:** {secondary_data['population']:,}")
                    st.write(f"**Area:** {secondary_data['area']:,} km²")
                    st.write(f"**Languages:** {', '.join(secondary_data['languages']) or 'Unknown'}")
                    st.write(f"**Currencies:** {', '.join(secondary_data['currencies']) or 'Unknown'}")
                else:
                    st.warning(
                        f"Could not load data for '{secondary_country}'. "
                        "The insight will only use the primary country."
                    )
            else:
                st.info("Enable the comparison checkbox in the sidebar to add a second country.")

# ----- TAB 2: AI INSIGHT -----
with insight_tab:
    with st.container():
        st.subheader("🧠 AI-Generated Country Insight")
        st.write(
            "Click the button below to ask Gemini to analyze the selected country (and optional comparison "
            "country) and generate a custom insight."
        )

        st.markdown("---")

        if st.button("✨ Generate Country Insight"):
            if not primary_data:
                st.error("Please fix the primary country name before generating an insight.")
            else:
                with st.spinner("Asking Gemini to analyze the country data..."):
                    insight_text = generate_country_insight(
                        primary_data=primary_data,
                        secondary_data=secondary_data,
                        insight_type=insight_type,
                        detail_level=detail_level,
                        extra_note=extra_note,
                    )
                st.markdown("### Insight")
                st.write(insight_text)
        else:
            st.info("Set your options in the sidebar, then click **Generate Country Insight** to see the AI output.")

# ---------- FOOTER CONTAINER ----------
with st.container():
    st.markdown("---")
    st.caption("✨ Phase 3: Country Insight • REST Countries API + Google Gemini")
