import streamlit as st
import requests
import google.generativeai as genai

# ---------- Page config ----------
st.set_page_config(
    page_title="Country Chatbot",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Country Chatbot (Phase 4)")
st.write(
    "Ask questions about countries and I'll answer using live data from the REST Countries API "
    "plus Google Gemini. I remember our conversation as we go."
)

# ---------- Configure Gemini ----------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
    GEMINI_READY = True
except Exception as e:
    GEMINI_READY = False
    st.error("⚠️ Gemini is not configured correctly. Please set GEMINI_API_KEY in Streamlit secrets.")
    

# ---------- Helper: fetch country data ----------
BASE_URL = "https://restcountries.com/v3.1"

def get_country_data(country_name: str):
    """
    Fetch basic data about a country from the REST Countries API.
    You can customize which fields you care about.
    """
    if not country_name:
        return None

    try:
        response = requests.get(f"{BASE_URL}/name/{country_name}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                country = data[0]
                # Extract a subset of fields you want the chatbot to use
                return {
                    "name": country.get("name", {}).get("common"),
                    "official_name": country.get("name", {}).get("official"),
                    "capital": country.get("capital", ["Unknown"])[0],
                    "region": country.get("region", "Unknown"),
                    "subregion": country.get("subregion", "Unknown"),
                    "population": country.get("population", 0),
                    "area": country.get("area", 0),
                    "languages": list((country.get("languages") or {}).values()),
                    "currencies": list((country.get("currencies") or {}).keys()),
                    "flag_emoji": country.get("flag", "")
                }
    except Exception:
        # You can log the error if you want
        return None

    return None


# ---------- Helper: build prompt for Gemini ----------
def build_prompt(chat_history, country_data, user_message):
    """
    Convert the chat history + structured country data into a single prompt string.
    You should customize the instructions so the chatbot behaves how you want.
    """
    system_instructions = (
        "You are a helpful assistant that answers questions about countries using the structured "
        "data I provide from the REST Countries API. "
        "If something is not in the data, you may answer from general knowledge, but say that it "
        "is not directly from the API. "
        "Keep answers clear and friendly. "
    )

    # Turn previous messages into a conversation transcript
    history_str = ""
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        history_str += f"{role.upper()}: {content}\n"

    # Include structured country info (if any)
    country_info_str = "No country data was provided."
    if country_data:
        country_info_str = f"""
Country data:
- Name: {country_data.get('name')}
- Official Name: {country_data.get('official_name')}
- Capital: {country_data.get('capital')}
- Region: {country_data.get('region')}
- Subregion: {country_data.get('subregion')}
- Population: {country_data.get('population')}
- Area: {country_data.get('area')} km²
- Languages: {', '.join(country_data.get('languages', []))}
- Currencies: {', '.join(country_data.get('currencies', []))}
- Flag: {country_data.get('flag_emoji', '')}
"""

    prompt = f"""
{system_instructions}

Conversation so far:
{history_str}

Structured REST Countries API info:
{country_info_str}

User's latest question:
{user_message}

Now respond as the assistant. Be concise but informative.
"""
    return prompt


# ---------- Helper: call Gemini with error handling ----------
def ask_gemini(prompt: str) -> str:
    """
    Call Gemini safely. Wrap in try/except and return a user-friendly error message on failure.
    """
    if not GEMINI_READY:
        return "Gemini is not available right now. Please contact the app owner."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # You can log e for debugging if desired
        return "Sorry, something went wrong while contacting the AI. Please try again in a moment."


# ---------- Initialize chat history in session_state ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Optional: Let user pick a 'focus country' for the chatbot
st.sidebar.header("Chatbot Settings")
default_country = "France"
selected_country = st.sidebar.text_input(
    "Focus country (optional):",
    value=default_country,
    help="The chatbot will use data for this country when answering your questions."
)

country_data = get_country_data(selected_country) if selected_country else None
if selected_country and not country_data:
    st.sidebar.warning(f"Could not load data for '{selected_country}'. The chatbot may answer more generally.")

# ---------- Display chat history ----------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat input ----------
user_message = st.chat_input("Ask me something about countries...")

if user_message:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    # Build prompt using full history + current country data
    prompt = build_prompt(
        chat_history=st.session_state.chat_history,
        country_data=country_data,
        user_message=user_message
    )

    # Call Gemini with error handling
    assistant_reply = ask_gemini(prompt)

    # Add assistant reply to history and display it
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# Footer
st.markdown("---")
st.caption("💡 Phase 4: Country Chatbot • Powered by Google Gemini and REST Countries API")
