from utils import (
    extract_resume_text,
    preprocess_text,
    extract_skills,
    find_missing_skills,
    calculate_match_score,
    skill_match_score,
    generate_suggestions
)

jd = """
Looking for a Data Science Intern.

Skills Required:
Python
SQL
Machine Learning
Docker
AWS
Pandas
""" 

text = extract_resume_text("sample_resume.pdf")

clean_text = preprocess_text(text)

skills = extract_skills(clean_text)

jd_clean = preprocess_text(jd)

jd_skills = extract_skills(jd_clean)

missing = find_missing_skills(skills, jd_skills)

resume_skill_text = " ".join(skills)
jd_skill_text = " ".join(jd_skills)

print("Skills in resume : ",skills)
print("Job description skills ; ", jd_skills)
print("Missing Skills:", missing)

score1 = skill_match_score(skills,jd_skills)
score2 = calculate_match_score(resume_skill_text,jd_skill_text)

print(f"Skills Match Score : {score1}%")
print(f"Match Score using cosine similarity : {score2}%")

suggestions = generate_suggestions(missing)

print("\nSuggestions:")

for s in suggestions:
    print("-", s)

