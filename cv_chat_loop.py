import json
import subprocess

CLOUD_FUNCTION_URL = "https://us-central1-christinevalmy.cloudfunctions.net/cv-gemini-2-5-bucket"
HISTORY_FILE = "history.json"
USER_ID = "12"
THREAD_ID = "12"

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def send_message(message, history):
    payload = {
        "message": message,
        "user_id": USER_ID,
        "thread_id": THREAD_ID,
        "history": history
    }

    curl_command = [
        "curl", "-s", "-X", "POST", CLOUD_FUNCTION_URL,
        "-H", f"Authorization: Bearer {subprocess.getoutput('gcloud auth print-identity-token')}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    result = subprocess.run(curl_command, capture_output=True, text=True)
    try:
        response_json = json.loads(result.stdout)
        return response_json.get("response", "[No response]")
    except json.JSONDecodeError:
        print("⚠️ Error: Couldn't decode JSON")
        print("Raw response:", result.stdout)
        return "[Error from API]"

def chat_loop():
    history = load_history()

    print("Chat started (type 'exit' to quit)\n")
    while True:
        user_message = input("You: ").strip()
        if user_message.lower() in ("exit", "quit"):
            break

        # Append user message to history
        history.append({"role": "user", "text": user_message})

        assistant_reply = send_message(user_message, history)
        print("Bot:", assistant_reply)

        # Append assistant reply to history
        history.append({"role": "assistant", "text": assistant_reply})

        save_history(history)

    print("✅ Chat ended.")

if __name__ == "__main__":
    chat_loop()

