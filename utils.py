import re
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills import SKILLS

def extract_resume_text(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text
 
def preprocess_text(text):
    text = text.lower()

    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found_skills.append(skill)

    return found_skills


def find_missing_skills(resume_skills, jd_skills):
    return list(set(jd_skills) - set(resume_skills))


def calculate_match_score(resume_text, jd_text):
    
    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([resume_text, jd_text])

    similarity = cosine_similarity(vectors[0:1],vectors[1:2])

    return round(similarity[0][0] * 100, 2)


def skill_match_score(resume_skills, jd_skills):
    
    matched = set(resume_skills) & set(jd_skills)

    score = (len(matched) / len(jd_skills)) * 100
    print("Matched : ",matched)
    print("Len of matched : ",len(matched))
    print("len of jd skills : ",len(jd_skills))

    return round(score, 2)

def generate_suggestions(missing_skills):
    
    suggestions = {
        "sql": "Learn SQL and include a database project.",
        "docker": "Learn Docker and containerize one of your projects.",
        "aws": "Gain exposure to AWS cloud services and deployment.",
        "tensorflow": "Build a deep learning project using TensorFlow.",
        "machine learning": "Add ML projects to demonstrate practical skills."
    }

    result = []

    for skill in missing_skills:
        skill = skill.lower()

        if skill in suggestions:
            result.append(suggestions[skill])

    return result