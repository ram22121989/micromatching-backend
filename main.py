from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Profile(BaseModel):
    username: str

@app.post("/engagement")
def get_engagement(data: Profile):
    try:
        url = f"https://www.instagram.com/{data.username}/?__a=1&__d=dis"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {"error": "Could not fetch data. Try again later."}

        user = res.json().get("graphql", {}).get("user", {})
        followers = user.get("edge_followed_by", {}).get("count", 0)
        posts = user.get("edge_owner_to_timeline_media", {}).get("edges", [])

        total_likes = 0
        total_comments = 0
        count = 0

        for post in posts[:10]:
            node = post.get("node", {})
            total_likes += node.get("edge_liked_by", {}).get("count", 0)
            total_comments += node.get("edge_media_to_comment", {}).get("count", 0)
            count += 1

        if count == 0 or followers == 0:
            return {"error": "Not enough data to calculate."}

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
