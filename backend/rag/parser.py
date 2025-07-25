import fitz  # PyMuPDF
from typing import Optional, List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from rag.skill_categories import CATEGORIES

# Load key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from all pages of a PDF file using PyMuPDF.

    Args:
        file_path (str): Path to the resume PDF.

    Returns:
        str: Concatenated text from all pages.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_structured_info(raw_text: str) -> Optional[dict]:
    """
    Uses OpenAI's updated SDK (>=1.0) to extract structured info from resume.
    """
    prompt = (
        "Extract technical skills, experience summaries, and any projects from this resume text. "
        "Return only valid JSON with keys: skills (list), experience (list), projects (list).\n\n"
        f"Resume:\n{raw_text[:3000]}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("JSON parse error:", e)
        print("Raw content:\n", content)
        return None
    except Exception as e:
        print("OpenAI API error:", e)
        return None
    
def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorizes a flat list of skills into predefined categories.

    Args:
        skills (List[str]): Extracted skills from the resume.

    Returns:
        Dict[str, List[str]]: Skills grouped by category.
    """
    categorized = {category: [] for category in CATEGORIES}

    for skill in skills:
        found = False
        for category, keywords in CATEGORIES.items():
            if skill in keywords:
                categorized[category].append(skill)
                found = True
                break
        if not found:
            categorized["Other"].append(skill)

    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}