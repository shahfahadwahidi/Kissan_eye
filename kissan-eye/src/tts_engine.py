import io
import re
from gtts import gTTS


def sanitize_for_speech(text: str) -> str:
    """
    Removes ALL markdown, symbols, and formatting tokens
    that gTTS would mispronounce as English words.
    Run this BEFORE passing any text to TTS.
    """

    # 1. Remove bold+italic markers (*** or ___)
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'_{1,3}', '', text)

    # 2. Remove markdown headers (##, ###, ####)
    text = re.sub(r'#{1,6}\s*', '', text)

    # 3. Remove markdown bullet points (-, *, •)
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)

    # 4. Remove numbered lists (1. 2. 3.)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # 5. Remove inline code backticks
    text = re.sub(r'`{1,3}', '', text)

    # 6. Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # 7. Remove emoji (keep Urdu/Arabic unicode safe)
    text = re.sub(
        r'[\U00010000-\U0010ffff'
        r'\U0001F600-\U0001F64F'
        r'\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF]',
        '', text, flags=re.UNICODE
    )

    # 8. Remove section dividers (---, ===, ___)
    text = re.sub(r'[-=_]{3,}', '', text)

    # 9. Remove bracket formatting ([text] or (text))
    text = re.sub(r'\[([^\]]*)\]', r'\1', text)
    text = re.sub(r'\(([^)]*)\)', r'\1', text)

    # 10. Remove colon-heavy label formatting
    #     e.g. " Bimari/Masla:" → "Bimari Masla"
    text = re.sub(r'[:/\\|]', ' ', text)

    # 11. Collapse multiple spaces and blank lines
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # 12. Strip leading/trailing whitespace
    text = text.strip()

    return text


def speak(text: str) -> bytes:
    """
    Converts Roman Urdu / Urdu text to speech.
    Sanitizes markdown BEFORE passing to gTTS.
    Returns MP3 bytes or None on failure.
    """
    try:
        # Always sanitize first — never pass raw LLM output to TTS
        clean_text = sanitize_for_speech(text)

        if not clean_text:
            print("⚠️  TTS skipped — text was empty after sanitization.")
            return None

        # Debug: print what gTTS actually receives
        print(f"️  TTS Input (sanitized):\n{clean_text[:300]}...")

        tts    = gTTS(text=clean_text, lang="ur", slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()

    except Exception as e:
        print(f" TTS Error: {e}")
        return None


def test_sanitizer():
    """
    Run this to verify the sanitizer works before deployment.
    python -c "from src.tts_engine import test_sanitizer; test_sanitizer()"
    """
    test_cases = [
        ("**Ilaj:** Spray karein",          "Ilaj Spray karein"),
        ("***Dimethoate*** use karein",      "Dimethoate use karein"),
        ("## Bimari\n- Pattay peele hain",   "Bimari\nPattay peele hain"),
        (" **Masla:** fungal infection",   "Masla fungal infection"),
        ("1. Pehle spray karein\n2. Phir...", "Pehle spray karein\nPhir..."),
    ]

    print("─── Sanitizer Test Results ───")
    all_passed = True
    for raw, expected in test_cases:
        result  = sanitize_for_speech(raw)
        passed  = "" if expected.strip() in result else ""
        if "" in passed:
            all_passed = False
        print(f"{passed} Input:    {repr(raw)}")
        print(f"   Output:   {repr(result)}")
        print(f"   Expected: {repr(expected)}\n")

    print("─── All tests passed  ───" if all_passed
          else "─── Some tests failed  ───")
