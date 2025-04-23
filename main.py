from fastapi import FastAPI
from pydantic import BaseModel
import instaloader

app = FastAPI()
L = instaloader.Instaloader()

class Profile(BaseModel):
    username: str

@app.post("/engagement")
def get_engagement(data: Profile):
    try:
        profile = instaloader.Profile.from_username(L.context, data.username)
        followers = profile.followers
        posts = profile.get_posts()

        total_likes = 0
        total_comments = 0
        count = 0

        for post in posts:
            if count >= 10:
                break
            total_likes += post.likes
            total_comments += post.comments
            count += 1

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
