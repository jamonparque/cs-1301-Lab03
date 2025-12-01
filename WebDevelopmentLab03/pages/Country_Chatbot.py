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
    st.error(f"Debug info (Gemini config): {e}")

# ---------- REST Countries Helper ----------
BASE_URL = "https://restcountries.com/v3.1"

def get_country_data(country_name: str):
    """Fetch structured country data from REST Countries API."""
    if not country_name:
        return None

    try:
        response = requests.get(f"{BASE_URL}/name/{country_name}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                country = data[0]
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
        # If anything goes wrong with the API, just return None
        return None

    return None

# ---------- Prompt Builder ----------
def build_prompt(chat_history, country_data, user_message):
    """Builds a complete prompt for Gemini with structured data + chat history."""
    system_instructions = (
        "You are a helpful assistant that answers questions about countries using data from the "
        "REST Countries API. If a detail is not included in the provided data, you may answer from "
        "general knowledge but state that it is not directly from the API. Keep responses clear, "
        "accurate, and friendly."
    )

    # Convert chat history into a readable transcript
    history_str = ""
    for msg in chat_history:
        history_str += f"{msg['role'].upper()}: {msg['content']}\n"

    # Structured data section
    if country_data:
        country_info_str = f"""
Country data from REST Countries API:
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
    else:
        country_info_str = "No country data available."

    # Final prompt
    prompt = f"""
{system_instructions}

Conversation so far:
{history_str}

Structured REST Countries API info:
{country_info_str}

User's latest question:
{user_message}

Now respond as the assistant.
"""
    return prompt

# ---------- Gemini API Wrapper (KEY PART) ----------
def ask_gemini(prompt: str) -> str:
    """
    Safely call Gemini.
    - If Gemini isn't configured, tell the user.
    - If Gemini throws an error, show the real error (for debugging) AND a friendly message.
    """
    if not GEMINI_READY:
        return "Gemini is not available because the API key is not configured."

    try:
        response = model.generate_content(prompt)

        # Extra safety: sometimes response.text can be None
        if not hasattr(response, "text") or response.text is None:
            return "Gemini returned an empty response. Try asking in a different way."

        return response.text.strip()

    except Exception as e:
        # Show the real error in the UI for debugging
        st.error(f"Gemini API error: {e}")
        # Return a friendly message for the chat (assignment wants error handling)
        return (
            "Sorry, something went wrong while contacting the AI. "
            "Please try again in a moment."
        )

# ---------- Session State for Memory ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Sidebar Settings ----------
st.sidebar.header("Chatbot Settings")
selected_country = st.sidebar.text_input(
    "Focus country:",
    value="France",
    help="The chatbot will use data for this country when answering."
)

country_data = get_country_data(selected_country)
if selected_country and not country_data:
    st.sidebar.warning(f"Could not load data for '{selected_country}'. The chatbot may answer more generally.")

# ---------- Display Chat History ----------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat Input ----------
user_message = st.chat_input("Ask me something about countries...")

if user_message:
    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message
    })

    # Build prompt including all history + structured data
    prompt = build_prompt(
        chat_history=st.session_state.chat_history,
        country_data=country_data,
        user_message=user_message
    )

    # Ask Gemini
    assistant_reply = ask_gemini(prompt)

    # Save assistant message
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# ---------- Footer ----------
st.markdown("---")
st.caption("💡 Phase 4: Country Chatbot • Powered by Google Gemini and REST Countries API")
