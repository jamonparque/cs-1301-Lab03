import streamlit as st
import requests
import google.generativeai as genai

# ---------- Initialize Gemini ----------
@st.cache_resource
def init_gemini():
    """Initialize Gemini AI with error handling"""
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.sidebar.error("⚠️ GEMINI_API_KEY not found in secrets!")
            return None
        
        api_key = st.secrets["GEMINI_API_KEY"]
        
        # Validate key format
        if not api_key or not api_key.startswith("AIza"):
            st.sidebar.error("❌ Invalid API key format")
            return None
        
        # Configure with timeout
        genai.configure(api_key=api_key)
        
        # TRY THESE EXACT MODEL NAMES:
        models_to_try = [
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-latest",
            "gemini-1.0-pro-001",
            "gemini-1.5-pro-latest"
        ]
        
        for model_name in models_to_try:
            try:
                st.sidebar.info(f"Trying: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Simple test
                response = model.generate_content(
                    "Say 'Hello' in 3 words",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=100,
                        temperature=0.7
                    )
                )
                
                if response.text:
                    st.sidebar.success(f"✅ Success: {model_name}")
                    return model
                    
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    st.sidebar.warning(f"❌ {model_name}: Model not found")
                elif "429" in error_msg:
                    st.sidebar.warning(f"⚠️ {model_name}: Rate limit")
                else:
                    st.sidebar.warning(f"⚠️ {model_name}: {error_msg[:50]}")
                continue
        
        st.sidebar.error("❌ All models failed. Please check your API key and region.")
        return None
        
    except Exception as e:
        st.sidebar.error(f"❌ Setup error: {str(e)[:100]}")
        return None

# Initialize Gemini
gemini_model = init_gemini()

# ---------- Header ----------
st.markdown('<div class="main-header"><h1>🤖 AI-Powered Country Analysis</h1><p>Advanced country insights powered by Google Gemini AI</p></div>', unsafe_allow_html=True)

# ... rest of your Phase 3 code continues ...
