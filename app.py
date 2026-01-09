# app.py

from flask import Flask, render_template, request
import pickle
import numpy as np
import os
import re
import html
import urllib.parse
from markupsafe import Markup

# -------------------- Flask App --------------------
app = Flask(__name__)

# -------------------- Configuration --------------------
from config import DevelopmentConfig, ProductionConfig

env = os.getenv("APP_ENV", "development").lower()
if env == "production":
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_DIR = app.config.get("MODEL_DIR", os.path.join(BASE_DIR, "model"))
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# -------------------- Load Model --------------------
def load_pickle(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)

model = load_pickle(MODEL_PATH)
vectorizer = load_pickle(VECTORIZER_PATH)

# -------------------- Constants --------------------
SCAM_WORDS = ["urgent", "verify", "click", "password", "bank", "account", "login", "confirm"]

SHORT_DOMAINS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly"}
SUSPICIOUS_TLDS = {"xyz", "top", "cf", "ga", "ml", "tk", "biz", "info"}

URL_REGEX = re.compile(r"\b(?:https?://|www\.)[^\s<>()\"']+")

# -------------------- Helper Functions --------------------
def highlight_scam_words(text, keywords):
    escaped = html.escape(text)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b", re.IGNORECASE)
    highlighted = pattern.sub(r'<span class="highlight">\1</span>', escaped)
    return Markup(highlighted)

def extract_urls(text):
    return URL_REGEX.findall(text or "")

def analyze_url(url):
    parsed = urllib.parse.urlparse(url if url.startswith("http") else "http://" + url)
    host = parsed.netloc.lower()
    reasons = []
    suspicious = False

    if host.split(".")[-1] in SUSPICIOUS_TLDS:
        suspicious = True
        reasons.append("Suspicious TLD")

    if any(d in host for d in SHORT_DOMAINS):
        suspicious = True
        reasons.append("Shortened URL")

    return {
        "url": url,
        "status": "suspicious" if suspicious else "safe",
        "reasons": reasons or ["None"]
    }

def analyze_urls(text):
    return [analyze_url(u) for u in extract_urls(text)]

def bump_risk(risk):
    if risk == "LOW RISK":
        return "MEDIUM RISK"
    if risk == "MEDIUM RISK":
        return "HIGH RISK"
    return risk

# -------------------- Route --------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    risk = ""
    confidence = 0
    words = []
    highlighted_email = ""
    url_results = []

    if request.method == "POST":
        email = request.form["email"]

        vector = vectorizer.transform([email])
        prediction = model.predict(vector)[0]
        probability = model.predict_proba(vector)[0]

        confidence = round(max(probability) * 100, 2)
        words = [w for w in SCAM_WORDS if w in email.lower()]
        highlighted_email = highlight_scam_words(email, SCAM_WORDS)
        url_results = analyze_urls(email)

        if prediction == 1:
            result = "🚨 Scam / Phishing Email Detected"
            risk = "HIGH RISK" if confidence > 80 else "MEDIUM RISK"
        else:
            result = "✅ Safe Email"
            risk = "LOW RISK"

        if any(u["status"] == "suspicious" for u in url_results):
            risk = bump_risk(risk)

    return render_template(
        "index.html",
        result=result,
        risk=risk,
        confidence=confidence,
        words=words,
        highlighted_email=highlighted_email,
        url_results=url_results
    )

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True)
