
"""
This part is for testing the functions whether they are giving the expected output.
"""

from utils import (
    extract_resume_text,
    preprocess_text,
    extract_skills,
    find_missing_skills,
    calculate_match_score,
    skill_match_score,
    generate_suggestions,
    extract_experience,
    experience_score
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
    
print(extract_experience("2-4 years experience")) 
print(extract_experience("3 to 5 years")) 
print(extract_experience("Minimum 2 years")) 
print(extract_experience("At least 1 year")) 
print(extract_experience("3+ years")) 
print(extract_experience("5 years of experience")) 
print(extract_experience("1.5 yrs")) 
print(extract_experience("Freshers can apply")) 
print(extract_experience("two years of experience")) 
print(extract_experience("atleast four years of experience"))
print(extract_experience("applicants can have at least two to four years of experience"))
print(extract_experience("can have bw two to four years of experience"))
print(experience_score((2,2), (1,3))) 
print(experience_score((0,0), (1,3))) 
print(experience_score((5,5), (1,3)))
print(experience_score((4,4), (3,None))) 
print(experience_score((2,2), (3,None)))  
print(experience_score((5,5), (5,5)))      

