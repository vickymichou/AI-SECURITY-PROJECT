import requests
import datetime
import os
import time
import json
import sqlite3
from dotenv import load_dotenv
from llm_guard.input_scanners import PromptInjection

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

LOG_FILE = "security_audit.jsonl"
DB_FILE = "security_events.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            risk_score REAL NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT,
            model TEXT NOT NULL,
            source TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def log_event_json(event: dict):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def log_event_db(event: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO security_events (
            timestamp, status, risk_score, prompt, response, model, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event["timestamp"],
        event["status"],
        event["risk_score"],
        event["prompt"],
        event["response"],
        event["model"],
        event["source"]
    ))

    conn.commit()
    conn.close()


def save_event(event: dict):
    log_event_json(event)
    log_event_db(event)


init_db()

try:
    scanner = PromptInjection()
    print("\n✅ Scanner Initialized Successfully")
except Exception as e:
    print(f"❌ Scanner Error: {e}")
    scanner = None

if not API_KEY:
    print("❌ Δεν βρέθηκε GEMINI_API_KEY στο .env")
    raise SystemExit(1)

print("===================================================")
print("🛡️   SECURE AI CHATBOT - SQLITE PIPELINE MODE   🛡️")
print("===================================================\n")

while True:
    user_prompt = input("User > ")

    if user_prompt.lower() in ["exit", "quit"]:
        break
    if not user_prompt.strip():
        continue

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk = 0.0
    status = "ALLOWED"
    ai_response = None

    if scanner:
        print("[🔍] Scanning...")
        try:
            _, is_safe, risk = scanner.scan(user_prompt)

            if risk > 0.7:
                status = "BLOCKED"
            elif risk > 0.4:
                status = "ALERT"
            else:
                status = "ALLOWED"

            if status == "BLOCKED":
                print(f"🚨 BLOCKED! Risk: {risk:.2f}")

                event = {
                    "timestamp": timestamp,
                    "status": status,
                    "risk_score": max(round(risk, 2), 0),
                    "prompt": user_prompt,
                    "response": None,
                    "model": MODEL,
                    "source": "cli_chatbot"
                }

                save_event(event)
                continue

            elif status == "ALERT":
                print(f"⚠️ ALERT! Risk: {risk:.2f}")

        except Exception as e:
            print(f"❌ Scanner runtime error: {e}")
            continue

    print("✅ Sending request to AI...")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"\n🤖 AI > {ai_response}\n")
        else:
            status = "API_ERROR"
            print(f"❌ API Error {response.status_code}")
            print(response.text)

    except Exception as e:
        status = "REQUEST_FAILED"
        print(f"❌ Error: {e}")

    event = {
        "timestamp": timestamp,
        "status": status,
        "risk_score": max(round(risk, 2), 0),
        "prompt": user_prompt,
        "response": ai_response,
        "model": MODEL,
        "source": "cli_chatbot"
    }

    save_event(event)

    time.sleep(1)