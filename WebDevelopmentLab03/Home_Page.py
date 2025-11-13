import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Global Country Analytics",
    page_icon="🌍",
    layout="wide"
)

# Title of App
st.title("🌍 Global Country Analytics")

# Assignment Data 
# TODO: Fill out your team number, section, and team members
st.header("CS 1301 - Intro to Computing - Fall 2025")
st.subheader("Team 48, Web Development - Section C/D")
st.subheader("Aidan Berry, Jaemin Park")

st.markdown("---")

# Introduction
st.markdown("""
Welcome to our Global Country Analytics platform! This web application provides interactive 
exploration and analysis of country data from around the world using real-time API data.

Navigate between the pages using the sidebar to explore different features:

### 📋 Page Descriptions

1. **🌍 Country Analysis**: Interactive exploration of 250+ countries with real-time data visualization, 
   comparative analysis tools, and demographic insights using the REST Countries API.

### 🚀 Features
- Real-time data from REST Countries API
- Interactive charts and visualizations  
- Population trends and demographic analysis
- Regional comparisons and insights
- Customizable filters and sorting options
- Responsive design for all devices
""")

# Optional: Add some visual elements
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries Analyzed", "250+")
    
with col2:
    st.metric("Data Points", "10,000+")
    
with col3:
    st.metric("Real-time API", "REST Countries")

st.markdown("---")
st.info("💡 **Tip**: Use the sidebar navigation to explore the Country Analysis page and start analyzing global data!")
