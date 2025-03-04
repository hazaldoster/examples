from pydantic import BaseModel


class Tweet(BaseModel):
    content: str
    num_likes: int
    num_retweets_and_quotes: int
    num_replies: int
    published_at: str


class AllTweets(BaseModel):
    tweets: list[Tweet]


class AllFollowers(BaseModel):
    followers: list[str]


class AllFollowing(BaseModel):
    following: list[str]
