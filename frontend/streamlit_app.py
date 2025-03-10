# frontend/streamlit_app.py
import streamlit as st
import requests
import json

st.title("AI-Powered Job Recommender")

# User profile collection
with st.sidebar:
    st.header("Your Profile")
    user_id = st.text_input("Enter your User ID")
    skills = st.text_input("Your Skills (comma separated)")
    experience = st.text_input("Years of Experience")
    location = st.text_input("Preferred Location")
    preferences = st.text_area("Job Preferences (describe ideal job)")
    
    if st.button("Save Profile"):
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        payload = {
            "user_id": user_id,
            "skills": skill_list,
            "experience": experience,
            "location": location,
            "preferences": preferences
        }
        response = requests.post("http://127.0.0.1:8000/save_user_context/", params=payload)
        if response.status_code == 200:
            st.success("Profile saved successfully!")
        else:
            st.error("Failed to save profile")

# Job recommendations
st.header("Job Recommendations")
if st.button("Get Personalized Recommendations"):
    if not user_id:
        st.warning("Please enter your User ID")
    else:
        with st.spinner("Finding the perfect jobs for you..."):
            response = requests.get(f"http://127.0.0.1:8000/recommendations/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Display Claude's analysis
                st.subheader("AI Job Match Analysis")
                st.write(data.get("claude_analysis", "No analysis available"))
                
                # Display job recommendations
                st.subheader("Top Job Matches")
                for i, job in enumerate(data.get("recommendations", []), 1):
                    with st.expander(f"{i}. {job.get('title')} at {job.get('company', 'Company')}"):
                        st.write(f"**Location:** {job.get('location', 'Not specified')}")
                        st.write(f"**Description:** {job.get('description', 'No description available')}")
                        if 'url' in job:
                            st.markdown(f"[Apply Now]({job['url']})")
            else:
                st.error("Failed to get recommendations. Please ensure your profile is saved.")
