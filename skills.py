import pandas as pd

# df = pd.read_csv("Skill_dataset/all_data_skill_and_nonskills.csv")
# df = pd.read_csv("Skill_dataset/skills.csv")
# df = pd.read_excel("Skill_dataset/Technology Skills.xlsx")

skills_df = pd.read_csv("Skill_dataset/technical_skills.csv")
skills_df.drop('Skill ID',axis=1,inplace=True)

SKILLS = (
    skills_df.iloc[:, 0]
    .dropna()
    .str.lower()
    .unique()
    .tolist()
)

EXTRA_SKILLS = [
    "excel",
    "tableau",
    "power bi",
    "statistics",
    "data modeling",
    "business intelligence",
    "data cleaning",
    "data wrangling",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "tensorflow",
    "keras",
    "pytorch",
    "spark",
    "hadoop",
    "aws",
    "docker",
    "git",
    "github",
    "mongodb",
    "postgresql",
    "mysql"
]

SKILLS.extend(EXTRA_SKILLS)
SKILLS = list(set(SKILLS))
 
# print(skills_df.head(10))
# print("Shape and columns of skills_df :")
# print("shape : ",skills_df.shape)
# print("Columns : ",skills_df.columns)
# print("len of SKILLS : ",len(SKILLS))
print("excel" in SKILLS)
print("tableau" in SKILLS)
print("power bi" in SKILLS)
print("statistics" in SKILLS)