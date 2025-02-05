import os
import tweepy
import random
import time
import openai
import requests
import ffmpeg
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, jsonify, render_template
from textblob import TextBlob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
API_KEYS = {
    "API_KEY": os.getenv("API_KEY"),
    "API_SECRET": os.getenv("API_SECRET"),
    "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
    "ACCESS_SECRET": os.getenv("ACCESS_SECRET"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "UNSPLASH_ACCESS_KEY": os.getenv("UNSPLASH_ACCESS_KEY"),
}

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEYS["API_KEY"], API_KEYS["API_SECRET"])
auth.set_access_token(API_KEYS["ACCESS_TOKEN"], API_KEYS["ACCESS_SECRET"])
api = tweepy.API(auth)

# Initialize Flask app
app = Flask(__name__)

# Helper functions
def fetch_travel_image(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={API_KEYS['UNSPLASH_ACCESS_KEY']}"
    response = requests.get(url).json()
    return response.get("urls", {}).get("regular")

def generate_ai_tweet(prompt="Write an engaging travel tweet:"):
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=50
    )
    return response.choices[0].text.strip()

def send_travel_dm(user_id, message="Hey! 🌍 Here’s your daily travel inspiration. Stay adventurous! #TravelMore"):
    try:
        api.send_direct_message(user_id, message)
        return {"message": "DM sent successfully!"}
    except tweepy.TweepError as e:
        return {"error": str(e)}

def get_twitter_analytics():
    tweets = api.user_timeline(count=100)
    data = {
        "Retweets": [tweet.retweet_count for tweet in tweets],
        "Likes": [tweet.favorite_count for tweet in tweets]
    }
    return pd.DataFrame(data)

# Flask routes
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/analytics")
def analytics():
    df = get_twitter_analytics()
    df.plot(kind='bar', figsize=(10, 5))
    plt.title("Twitter Engagement Analytics")
    plt.xlabel("Tweet Index")
    plt.ylabel("Engagement Count")
    plt.savefig("static/analytics.png")
    return render_template("analytics.html", image_url="/static/analytics.png")

@app.route("/schedule_tweet", methods=["POST"])
def schedule_tweet():
    data = request.json
    tweet_text = data.get("text", "")
    image_query = data.get("image_query", "travel")
    image_url = fetch_travel_image(image_query)
    
    media_id = None
    if image_url:
        image_path = "scheduled_travel_image.jpg"
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as handler:
            handler.write(img_data)
        media = api.media_upload(image_path)
        media_id = [media.media_id]
    
    api.update_status(status=tweet_text, media_ids=media_id)
    return jsonify({"message": "Scheduled Tweet posted successfully!"})

@app.route("/upload_media", methods=["POST"])
def upload_media():
    file = request.files['file']
    file_path = f"static/{file.filename}"
    file.save(file_path)
    media = api.media_upload(file_path)
    return jsonify({"media_id": media.media_id_string})

@app.route("/generate_ai_tweet", methods=["POST"])
def generate_ai_tweet_route():
    data = request.json
    return jsonify({"tweet": generate_ai_tweet(data.get("prompt"))})

@app.route("/manage_auto_replies", methods=["POST"])
def manage_auto_replies():
    return jsonify({"message": "Auto-replies updated!", "enabled": request.json.get("enabled", True)})

@app.route("/manage_dm_newsletter", methods=["POST"])
def manage_dm_newsletter():
    return jsonify(send_travel_dm(request.json.get("user_id")))

@app.route("/api_keys", methods=["POST"])
def update_api_keys():
    for key in API_KEYS.keys():
        if key in request.json:
            os.environ[key] = request.json[key]
    return jsonify({"message": "API keys updated successfully!"})

@app.route("/backup_tweets", methods=["GET"])
def backup_tweets():
    tweets = api.user_timeline(count=100)
    tweets_data = [{"text": tweet.text, "created_at": str(tweet.created_at)} for tweet in tweets]
    df = pd.DataFrame(tweets_data)
    backup_file = "static/tweets_backup.csv"
    df.to_csv(backup_file, index=False)
    return jsonify({"message": "Tweets backed up successfully!", "backup_url": backup_file})

# Run the bot
if __name__ == "__main__":
    app.run(debug=True)
