from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client.github_events

# GitHub Webhook Secret (validate payloads)
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    # Handle Push, PR, Merge events
    if event_type == "push":
        author = data["pusher"]["name"]
        to_branch = data["ref"].split("/")[-1]
        timestamp = datetime.now().strftime("%d %B %Y - %I:%M %p UTC")
        commit_hash = data["head_commit"]["id"]

        db.events.insert_one({
            "request_id": commit_hash,
            "author": author,
            "action": "PUSH",
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    elif event_type == "pull_request":
        author = data["sender"]["login"]
        to_branch = data["pull_request"]["base"]["ref"]
        from_branch = data["pull_request"]["head"]["ref"]
        timestamp = datetime.now().strftime("%d %B %Y - %I:%M %p UTC")
        pr_id = str(data["pull_request"]["id"])

        db.events.insert_one({
            "request_id": pr_id,
            "author": author,
            "action": "PULL_REQUEST",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    return jsonify({"status": "success"}), 200

@app.route("/api/events", methods=["GET"])
def get_events():
    events = list(db.events.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(events)

if __name__ == "__main__":
    app.run(debug=True)
