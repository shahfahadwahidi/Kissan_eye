"""
Kissan-Eye API Test Script
Run with: python test_apis.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

# ─────────────────────────────────────────
# TEST 1: Environment Variables
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  TEST 1: Environment Variables")
print("="*50)

gemini_key = os.getenv("GEMINI_API_KEY")
gcp_project = os.getenv("GCP_PROJECT_ID")
gcp_location = os.getenv("GCP_LOCATION")
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

print(f"  GEMINI_API_KEY         : {'SET (' + gemini_key[:8] + '...)' if gemini_key and gemini_key != 'paste_your_gemini_key_here' else 'NOT SET or placeholder'}")
print(f"  GCP_PROJECT_ID         : {gcp_project or 'NOT SET'}")
print(f"  GCP_LOCATION           : {gcp_location or 'NOT SET'}")
print(f"  GOOGLE_APPLICATION_CREDENTIALS: {creds_path or 'NOT SET'}")

creds_file_exists = creds_path and os.path.exists(creds_path)
print(f"  Service account file   : {'Found at ' + creds_path if creds_file_exists else 'NOT FOUND — place your JSON in keys/'}")

# ─────────────────────────────────────────
# TEST 2: Gemini API (google-generativeai)
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  TEST 2: Gemini API (AI Studio key)")
print("="*50)

if not gemini_key or gemini_key == "paste_your_gemini_key_here":
    print(f"  {SKIP} No GEMINI_API_KEY set — skipping")
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'API is working' in one word.")
        print(f"  {PASS} Gemini API responded: {response.text.strip()}")
    except Exception as e:
        print(f"  {FAIL} Gemini API error: {e}")

# ─────────────────────────────────────────
# TEST 3: Vertex AI
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  TEST 3: Vertex AI")
print("="*50)

if not gcp_project:
    print(f"  {SKIP} GCP_PROJECT_ID not set — skipping")
elif not creds_file_exists:
    print(f"  {SKIP} service-account.json not found in keys/ — skipping")
else:
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=gcp_project, location=gcp_location or "us-central1")
        model = GenerativeModel("gemini-1.5-flash-001")
        response = model.generate_content("Say 'Vertex OK' in one word.")
        print(f"  {PASS} Vertex AI responded: {response.text.strip()}")
    except ImportError:
        print(f"  {FAIL} google-cloud-aiplatform not installed. Run: pip install google-cloud-aiplatform")
    except Exception as e:
        print(f"  {FAIL} Vertex AI error: {e}")

# ─────────────────────────────────────────
# TEST 4: gTTS (Text-to-Speech)
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  TEST 4: gTTS (Text-to-Speech)")
print("="*50)

try:
    from gtts import gTTS
    import io
    tts = gTTS(text="Salam", lang="ur")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    size = len(buf.getvalue())
    print(f"  {PASS} gTTS generated {size} bytes of audio")
except Exception as e:
    print(f"  {FAIL} gTTS error: {e}")

# ─────────────────────────────────────────
# TEST 5: PyMuPDF (PDF Loading)
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  TEST 5: PyMuPDF (PDF Loader)")
print("="*50)

try:
    import fitz
    print(f"  {PASS} PyMuPDF imported — version: {fitz.version[0]}")
    pdfs = [f for f in os.listdir("data/pdfs") if f.endswith(".pdf")]
    print(f"         PDFs found in data/pdfs/: {len(pdfs)} {'(' + ', '.join(pdfs) + ')' if pdfs else '(empty — add PDFs to enable context)'}")
except Exception as e:
    print(f"  {FAIL} PyMuPDF error: {e}")

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
print("\n" + "="*50)
print("  DONE — Fix any [FAIL] or [SKIP] items above.")
print("="*50 + "\n")
