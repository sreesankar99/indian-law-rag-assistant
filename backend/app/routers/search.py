import os
from dotenv import load_dotenv
# Load the .env file
load_dotenv()
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Section
from google import genai
from google.genai import types

# --- CACHE SETUP ---
# This dictionary will store our past answers to save API calls
# Format: { "query_language": "answer_text" }
answer_cache = {}

# PASTE YOUR API KEY HERE
GEMINI_API_KEY =os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Check your .env file.")


client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=1),
        timeout=15000,
    ),
)

router = APIRouter(prefix="/api")

class AskRequest(BaseModel):
    query: str
    language: str = "en"

# 1. IPC to BNS Mapping Dictionary
IPC_MAP = {
    "302": "103", "420": "318", "376": "63", "498a": "85", 
    "307": "109", "323": "115", "354": "74", "506": "351",
    "379": "303", "392": "309", "395": "310", "406": "316", "467": "335"
}

@router.post("/ask")
def ask_question(req: AskRequest, db: Session = Depends(get_db)):
    query_lower = req.query.lower()
    
    # 2. Detect Direct Lookups (e.g., "bns 303", "ipc 302", "article 21")
    direct_match = re.search(r'\b(bns|ipc|article)\s*[-:]?\s*(\d+[a-z]?)\b', query_lower)
    
    target_act = None
    target_section = None

    if direct_match:
        prefix = direct_match.group(1)
        num = direct_match.group(2)
        
        if prefix == "bns":
            target_act = "BNS"
            target_section = num
        elif prefix == "ipc":
            # If they ask for IPC, we intercept and send them to the BNS equivalent
            mapped_bns = IPC_MAP.get(num)
            if mapped_bns:
                target_act = "BNS"
                target_section = mapped_bns
            else:
                target_act = "IPC"
                target_section = num
        elif prefix == "article":
            target_act = "CONSTITUTION"
            target_section = num

    # 3. Handle Direct Lookup (Bypass AI completely)
    if target_act and target_section:
        section = db.query(Section).filter(
            Section.act == target_act,
            Section.section_no == target_section
        ).first()
        
        if section:
            if req.language == "hi":
                lang_text = "यहाँ कानून का पाठ है:"
            elif req.language == "ml":
                lang_text = "നിയമത്തിന്റെ കൃത്യമായ വാചകം ഇതാണ്:"
            else:
                lang_text = "Here is the exact text:"
                
            return {
                "answer": f"{lang_text} {section.act} Section {section.section_no} - {section.section_title}",
                "sections_used": [{
                    "act": section.act,
                    "section_no": section.section_no,
                    "title": section.section_title,
                    "text": section.text_en
                }]
            }
        else:
            return {
                "answer": f"Could not find {target_act} Section {target_section} in the database.",
                "sections_used": []
            }

    # 4. Standard RAG Pipeline (if not a direct number lookup)
    emb = client.models.embed_content(
        model="gemini-embedding-001",
        contents=req.query,
    )
    query_embedding = emb.embeddings[0].values

    results = db.query(Section).order_by(
        Section.embedding.cosine_distance(query_embedding)
    ).limit(3).all()

    context = ""
    for r in results:
        context += f"\n---\nAct: {r.act} Section {r.section_no}\nTitle: {r.section_title}\nText: {r.text_en}\n"

    if req.language == "hi":
        lang_name = "Hindi"
    elif req.language == "ml":
        lang_name = "Malayalam"
    else:
        lang_name = "English"
    prompt = f"""You are a legal assistant for Indian Law.
Use ONLY the provided context to answer. State any punishment mentioned.
Cite Act + Section number at the start.

IMPORTANT: You MUST reply in {lang_name}.

Context:
{context}

Question: {req.query}

Answer:"""

    # 5. Check Cache Before Calling AI
    cache_key = f"{req.query.lower().strip()}_{req.language}"
    
    if cache_key in answer_cache:
        print("⚡ Returning cached answer!")
        return {
            "answer": answer_cache[cache_key],
            "sections_used": [
                {
                    "act": r.act,
                    "section_no": r.section_no,
                    "title": r.section_title,
                    "text": r.text_en,
                }
                for r in results
            ],
        }

    # 6. Generate with AI (If not in cache)
    candidate_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
    response_text = None

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                # config=types.GenerateContentConfig(
                #     thinking_config=types.ThinkingConfig(thinking_budget=0),
                # ),
            )
            response_text = response.text
            break
        except Exception as e:
            print(f"❌ Failed {model_name}: {e}")
            continue

    if not response_text:
        response_text = "The AI model is temporarily busy. Please try again."

    # 7. Save to Cache for next time
    answer_cache[cache_key] = response_text

    return {
        "answer": response_text,
        "sections_used": [
            {
                "act": r.act,
                "section_no": r.section_no,
                "title": r.section_title,
                "text": r.text_en,
            }
            for r in results
        ],
    }

@router.get("/lookup/{act}/{section_no}")
def direct_lookup(act: str, section_no: str, db: Session = Depends(get_db)):
    act_upper = act.upper()
    if act_upper in ["COI", "ARTICLE"]:
        act_upper = "CONSTITUTION"
    
    section = db.query(Section).filter(
        Section.act == act_upper,
        Section.section_no == section_no
    ).first()

    if not section:
        return {"error": "Section not found in database"}

    return {
        "act": section.act,
        "section_no": section.section_no,
        "title": section.section_title,
        "text": section.text_en
    }