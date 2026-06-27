import streamlit as st
import pandas as pd

from utils import (
    extract_resume_text,
    preprocess_text,
    extract_skills,
    find_missing_skills,
    calculate_match_score,
    skill_match_score,
    generate_suggestions,
    experience_score,
    extract_experience,
    
)

st.set_page_config(
    page_title="Resume Intelligence System",
    page_icon="📄",
    layout="wide"
)

# Title
st.markdown(
    """
    <h1 style='color:lightgreen; text-align:center;'>
    Resume Intelligence System
    </h1>
    """,
    unsafe_allow_html=True
)

st.write("")

# Upload Resume
st.markdown(
    "<h3 style='color:orange;'>Upload Resume PDF</h3>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    accept_multiple_files=True
)

# Job Description
st.markdown(
    "<h3>Paste Job Description</h3>",
    unsafe_allow_html=True
)

jd = st.text_area(
    "",
    height=250,
    placeholder="Paste the Job Description here..."
)

st.write("")

# Analyze Button
analyze = st.button("Analyze Resume")

if analyze:

    if not uploaded_file:
        st.error("Please upload a resume.")
        st.stop()

    if not jd.strip():
        st.error("Please enter a Job Description.")
        st.stop()

    results = []

    # JD Processing
    jd_clean = preprocess_text(jd)
    jd_skills = extract_skills(jd_clean)
    jd_exp = extract_experience(jd_clean)

    for file in uploaded_file:

        resume_text = extract_resume_text(file)
        resume_clean = preprocess_text(resume_text)

        resume_skills = extract_skills(resume_clean)
        missing_skills = find_missing_skills(resume_skills,jd_skills)

        skill_score = skill_match_score(resume_skills,jd_skills)
        cosine_score = calculate_match_score(" ".join(resume_skills)," ".join(jd_skills))
        
        matched_skills = list(set(resume_skills) & set(jd_skills))
        resume_exp = extract_experience(resume_text)
        
        exp_score = experience_score(resume_exp,jd_exp)

        # debugging
        # print(file.name)
        # print("Resume Experience:", resume_exp)
        # print("JD Experience:", jd_exp)
        # print("Experience Score:", exp_score)
        # print("----------------------")

        results.append({
            "Resume": file.name,
            "ATS Match Score": skill_score*0.7+0.3*exp_score,
            "Matched Skills": len(matched_skills),
            "Missing Skills": missing_skills,

            # Detailed data
            "Resume Skills": resume_skills,
            "JD Skills": jd_skills,
            "Matched Skills List": matched_skills,
            "Experience": resume_exp,
            "Experience Score": exp_score,
        })

    # Store results AND the sorted DataFrame in session state
    df = pd.DataFrame(results)
    df = df.sort_values(
        by="ATS Match Score",
        ascending=False
    ).reset_index(drop=True)

    st.session_state["results"] = results
    st.session_state["display_df"] = df[["Resume", "ATS Match Score", "Matched Skills"]]
    st.session_state["top_resume"] = df.iloc[0].to_dict()


# ── Everything below runs on EVERY re-run, driven by session_state ──────────

if "results" in st.session_state:

    results   = st.session_state["results"]
    display_df = st.session_state["display_df"]
    top_resume = st.session_state["top_resume"]

    st.write("---")

    # Results Heading
    st.markdown(
        "<h2 style='color:orange;'>Results</h2>",
        unsafe_allow_html=True
    )

    st.subheader("🏆 Resume Ranking")
    st.dataframe(display_df)

    selected_resume = st.selectbox(
        "Select Resume for Detailed Analysis",
        display_df["Resume"]
    )

    # Look up the selected resume's data
    selected_data = next(
        item for item in results
        if item["Resume"] == selected_resume
    )

    # Skill Match Score
    st.markdown(
        f"""
        <h3 style='color:yellow;'>
        ATS Match Score: {selected_data['ATS Match Score']}%
        </h3>
        """,
        unsafe_allow_html=True
    )

    st.progress(selected_data["ATS Match Score"] / 100)

    st.success(
        f"🏆 Best Match: {top_resume['Resume']} "
        f"with a score of {top_resume['ATS Match Score']}%"
    )

    # Eligibility Message
    if selected_data["ATS Match Score"] >= 80:
        st.success(
            "🎉 Excellent Match! Your profile aligns very strongly with this role. "
            "You appear to be a highly competitive candidate. 🚀"
        )
    elif selected_data["ATS Match Score"] >= 60:
        st.info(
            "👍 Good Match! You meet many of the required skills. "
            "A few improvements could strengthen your profile further."
        )
    else:
        st.warning(
            "📚 There are some important skill gaps. "
            "Consider improving the missing areas listed below."
        )

    st.write("---")

    st.subheader("✅ Matched Skills")
    st.write(selected_data["Matched Skills List"])

    st.subheader("❌ Missing Skills")
    st.write(selected_data["Missing Skills"])

    st.subheader("📄 Resume Skills")
    st.write(selected_data["Resume Skills"])

    st.subheader("🎯 JD Skills")
    st.write(selected_data["JD Skills"])