import sys
import os
import time  
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Section
from google import genai

# PASTE YOUR FULL API KEY HERE
GEMINI_API_KEY =os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

Base.metadata.create_all(bind=engine)

def get_embedding(text: str):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"  Network error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("  Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise e


DATA = [
    {
        "section_id": "const_12",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "12",
        "section_title": "Definition of 'the State'",
        "text_en": "In this Part, unless the context otherwise requires, 'the State' includes the Government and Parliament of India and the Government and the Legislature of each of the States and all local or other authorities within the territory of India or under the control of the Government of India.",
        "plain_summary_en": "Defines what 'State' means for Fundamental Rights.",
        "keywords": ["state", "article 12", "government"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_14",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "14",
        "section_title": "Equality before law",
        "text_en": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
        "plain_summary_en": "Every person is equal before the law.",
        "keywords": ["equality", "article 14", "discrimination"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_19",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "19",
        "section_title": "Protection of freedom of speech",
        "text_en": "All citizens shall have the right to freedom of speech and expression; to assemble peaceably; to form associations; to move freely throughout the territory of India.",
        "plain_summary_en": "Citizens have the right to free speech and movement.",
        "keywords": ["freedom of speech", "article 19", "protest"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_21",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "21",
        "section_title": "Protection of life and personal liberty",
        "text_en": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
        "plain_summary_en": "Right to life and personal liberty.",
        "keywords": ["life", "liberty", "article 21"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_21A",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "21A",
        "section_title": "Right to education",
        "text_en": "The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.",
        "plain_summary_en": "Right to free education for children aged 6-14.",
        "keywords": ["education", "article 21A", "school"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_22",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "22",
        "section_title": "Protection against arrest and detention",
        "text_en": "No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest.",
        "plain_summary_en": "Rights of arrested persons.",
        "keywords": ["arrest", "detention", "article 22"],
        "ipc_corresponding": None,
    },
    {
        "section_id": "const_32",
        "act": "CONSTITUTION",
        "chapter_no": "III",
        "chapter_title": "Fundamental Rights",
        "section_no": "32",
        "section_title": "Right to constitutional remedies",
        "text_en": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed.",
        "plain_summary_en": "Right to approach Supreme Court if Fundamental Rights are violated.",
        "keywords": ["writ", "supreme court", "article 32", "remedies"],
        "ipc_corresponding": None,
    }
]


def seed_db():
    db = SessionLocal()
    try:
        count = 0
        for item in DATA:
            # 1. CHECK IF IT ALREADY EXISTS FIRST
            existing = db.query(Section).filter_by(section_id=item["section_id"]).first()
            if existing:
                print(f"Skipping {item['act']} {item['section_no']} (Already in DB)")
                continue

            # 2. IF NOT, EMBED AND INSERT
            print(f"Embedding and inserting: {item['act']} {item['section_no']}")
            content_to_embed = (
                f"Act: {item['act']}\n"
                f"Section: {item['section_no']}\n"
                f"Title: {item['section_title']}\n"
                f"Text: {item['text_en']}\n"
                f"Summary: {item['plain_summary_en']}"
            )
            vector = get_embedding(content_to_embed)
            section = Section(**item, embedding=vector)
            db.add(section)
            db.commit() # Commit one by one so we don't lose everything if the network drops
            count += 1

        print(f"Successfully added {count} new sections.")
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting DB Seed...")
    seed_db()