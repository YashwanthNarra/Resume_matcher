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
    
def experience_score(resume_exp, jd_exp):
    """
    Score how well the candidate's experience matches the JD requirement.
    
    resume_exp: (min_years, max_years) — from extract_experience on resume
    jd_exp:     (min_years, max_years) — from extract_experience on JD
    
    Returns a score 0-100.
    """
    jd_min, jd_max = jd_exp
    res_years, _ = resume_exp

    if jd_min == 0:
        return 100

    if res_years == 0:
        return 0

    if jd_max is None:
        if res_years >= jd_min:
            return 100
        return round((res_years / jd_min) * 100, 2)

    if jd_min <= res_years <= jd_max:
        return 100
    elif res_years < jd_min:
        return round((res_years / jd_min) * 100, 2)
    else:
        return max(70, round(100 - (res_years - jd_max) * 5, 2))
        

def _months_between(start_str, end_str):
    """Return months between two date strings like 'Apr 2019' or 'Present'."""
    from datetime import datetime
    MONTH_MAP = {
        "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
        "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
    }
    end_str = end_str.strip().lower()
    try:
        if "present" in end_str:
            end = datetime.now()
        else:
            parts = end_str.split()
            if len(parts) == 2:
                end = datetime(int(parts[1]), MONTH_MAP.get(parts[0][:3], 1), 1)
            elif len(parts) == 1 and parts[0].isdigit():
                end = datetime(int(parts[0]), 1, 1)
            else:
                return 0
        parts = start_str.strip().lower().split()
        if len(parts) == 2:
            start = datetime(int(parts[1]), MONTH_MAP.get(parts[0][:3], 1), 1)
        elif len(parts) == 1 and parts[0].isdigit():
            start = datetime(int(parts[0]), 1, 1)
        else:
            return 0
        return max(0, (end.year - start.year) * 12 + (end.month - start.month))
    except (ValueError, KeyError):
        return 0


def extract_experience(text):
    """
    Robust experience extractor for both resumes and job descriptions.

    Strategy (in priority order):
    1. Fresher / entry-level keywords → 0 years
    2. Summary headline "X years of experience" in first 500 chars → at-least X
    3. Compute total work experience from dated ranges, skipping
       Education / Academic Project / Certification / Internship sections
    4. JD-style range/plus patterns (e.g. "3-5 years", "2+ years")
    5. Fallback "X years" only when NOT preceded by contextual phrases
       like "period of", "over a", "past", "last" (avoids project descriptions)
    """
    text_lower = text.lower()

    word_to_num = {
        "zero":0,"one":1,"two":2,"three":3,"four":4,
        "five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10
    }
    for word, num in word_to_num.items():
        text_lower = re.sub(rf"\b{word}\b", str(num), text_lower)

    if re.search(r'\b(fresher|freshers|no experience required|entry.?level)\b', text_lower):
        return (0.0, 0.0)

    summary = text_lower[:500]
    m = re.search(
        r'(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+(?:\w+\s+){0,3}experience',
        summary
    )
    if m:
        return (float(m.group(1)), None)

    NON_WORK_RE = re.compile(
        r'^\s*(education|academic\s+project|internship|course|certification|'
        r'award|skill|publication|volunteer|project experience)\s*$',
        re.IGNORECASE
    )
    WORK_SECTION_RE = re.compile(
        r'^\s*(work\s+experience|professional\s+experience|employment|'
        r'experience|work\s+history|business\s+experience|career\s+history|'
        r'relevant\s+experience)\s*$',
        re.IGNORECASE
    )
    DATE_RANGE_RE = re.compile(
        r'(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|\d{4})'
        r'\s*[-–]\s*'
        r'(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}'
        r'|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'
        r'|\d{4}|present)'
        r'(?:\d{1,2}/\d{4})'
        r'\s*[-–]\s*'
        r'(?:\d{1,2}/\d{4}|present)',
        re.IGNORECASE
    )

    lines = text.split('\n')
    current_section = "unknown"
    work_months = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        stripped_lower = stripped.lower()

        if WORK_SECTION_RE.match(stripped):
            current_section = "work"
            continue
        if NON_WORK_RE.match(stripped):
            current_section = "non_work"
            continue

        for match in DATE_RANGE_RE.finditer(line):
            raw = match.group(0)
            parts = re.split(r'\s*[-–]\s*', raw, maxsplit=1)
            if len(parts) != 2:
                continue
            months = _months_between(parts[0], parts[1])
            if months <= 0:
                continue

            context_lines = lines[max(0, i-3):i+2]
            context_text = " ".join(context_lines).lower()
            is_education = bool(re.search(
                r'\b(university|college|school|bachelor|master|b\.?tech|m\.?tech'
                r'|b\.?e\b|m\.?s\b|gpa|degree|phd|course)\b',
                context_text
            ))
            is_project = bool(re.search(
                r'\b(academic project|personal project)\b',
                context_text
            ))

            if current_section == "work" and not is_education and not is_project:
                work_months.append(months)
            elif current_section == "unknown" and not is_education and not is_project:
                next_lines = " ".join(lines[i+1:i+3]).lower()
                if re.search(r'\b(analyst|engineer|developer|manager|intern|ltd|pvt|inc|corp|llc)\b', next_lines):
                    work_months.append(months)

    if work_months:
        total_years = round(sum(work_months) / 12, 1)
        return (total_years, total_years)

    m = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', text_lower)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    m = re.search(r'(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)', text_lower)
    if m:
        return (float(m.group(1)), None)
    m = re.search(r'(?:minimum|min|at\s*least|atleast)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', text_lower)
    if m:
        return (float(m.group(1)), None)

    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', text_lower):
        prefix = text_lower[max(0, m.start()-35):m.start()]
        if not re.search(
            r'\b(period of|over a|over the|past|last|more than|for the|nearly|almost|spanning)\b',
            prefix
        ):
            return (float(m.group(1)), float(m.group(1)))

    return (0.0, 0.0)