from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Profile(BaseModel):
    username: str

# Replace with your Apify credentials
APIFY_TASK_ID = "t5hs4wpbX548cOpm0"
APIFY_TOKEN = "apify_api_9rYa4B2ObxEiYiMYqwqm8ottDMh2sB2O88c4"

@app.post("/engagement")
def get_engagement(data: Profile):
    try:
        # 1. Run the Apify task
        start_url = f"https://api.apify.com/v2/actor-tasks/{APIFY_TASK_ID}/runs?token={APIFY_TOKEN}"
        run = requests.post(start_url, json={
            "usernames": [data.username]
        }).json()

        run_id = run["data"]["id"]

        # 2. Poll Apify until task is done
        for _ in range(20):
            time.sleep(2)
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            run_status = requests.get(status_url).json()
            if run_status["data"]["status"] == "SUCCEEDED":
                break

        # 3. Get the results
        dataset_id = run_status["data"]["defaultDatasetId"]
        data_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&clean=true"
        result = requests.get(data_url).json()

        if not result:
            return {"error": "No data returned from Apify"}

        user = result[0]
        followers = user["followersCount"]
        posts = user["latestPosts"][:10]

        total_likes = sum(p["likesCount"] for p in posts)
        total_comments = sum(p["commentsCount"] for p in posts)
        count = len(posts)

        avg_likes = total_likes / count
        avg_comments = total_comments / count
        engagement_rate = (total_likes + total_comments) / (followers * count) * 100

        tier = "Low"
        if engagement_rate > 1: tier = "Average"
        if engagement_rate > 3: tier = "Good"
        if engagement_rate > 6: tier = "Excellent"

        return {
            "followers": followers,
            "avg_likes": int(avg_likes),
            "avg_comments": int(avg_comments),
            "engagement_rate": round(engagement_rate, 2),
            "tier": tier
        }

    except Exception as e:
        return {"error": str(e)}
