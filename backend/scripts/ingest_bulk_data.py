import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine, Base
from app.models import Section
from google import genai
from datasets import load_dataset

# PASTE YOUR API KEY HERE
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

Base.metadata.create_all(bind=engine)

def get_embedding(text: str):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values

def ingest_bns_data():
    print("Downloading BNS dataset from Hugging Face...")
    # This dataset contains BNS, BNSS, and BSA. We filter for BNS only.
    dataset = load_dataset("GSMS-B/indian-legal-sections-bns-bnss-bsa-2023", split="train")
    
    db = SessionLocal()
    try:
        # Optional: Clear old data to avoid duplicates during testing
        db.query(Section).delete()
        db.commit()
        
        count = 0
        # Filter for BNS sections only
        for row in dataset:
            if row.get("act") != "BNS 2023":
                continue
                
            section_no = str(row.get("section_number", ""))
            if not section_no:
                continue
                
            # Check if this section already exists to avoid re-embedding
            existing = db.query(Section).filter_by(section_id=f"bns_{section_no}").first()
            if existing:
                print(f"Skipping BNS Section {section_no} (Already in DB)")
                continue
            
            print(f"Processing BNS Section {section_no}: {title[:50]}...")
            
            # Create the text block for embedding
            content_to_embed = f"Act: BNS\nSection: {section_no}\nTitle: {title}\nChapter: {chapter}\nText: {text}"
            
            try:
                vector = get_embedding(content_to_embed)
            except Exception as e:
                print(f"  Embedding failed for Section {section_no}: {e}")
                time.sleep(5) # Wait if we hit rate limits
                continue

            # Create the database record
            section = Section(
                section_id=f"bns_{section_no}",
                act="BNS",
                chapter_no="", # Dataset doesn't always provide chapter number, but title is there
                chapter_title=chapter,
                section_no=section_no,
                section_title=title,
                text_en=text,
                plain_summary_en="", # We can generate these later if needed
                keywords=[], # We can generate these later if needed
                ipc_corresponding=None, # We'll handle IPC mapping separately
                embedding=vector
            )
            db.add(section)
            db.commit()
            count += 1
            
            # IMPORTANT: Sleep to respect API rate limits (free tier is 5 requests/min for some models)
            time.sleep(2) 

        print(f"Successfully ingested {count} BNS sections.")

    finally:
        db.close()

if __name__ == "__main__":
    ingest_bns_data()