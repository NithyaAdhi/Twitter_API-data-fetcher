import tweepy
import os
import json
import time
import random

def get_all_tweets(user_id, bearer_token, max_retries=5):
    """
    Retrieves and returns all available tweets for a given user ID with rate limit handling.
    """
    client = tweepy.Client(bearer_token)
    tweets = []
    max_results = 10
    retries = 0
    next_token = None
    response = {} # Initialize response here to handle cases where the try block fails the first time.

    while retries <= max_retries:
        try:
            response = client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                pagination_token=next_token,
                tweet_fields=["created_at", "public_metrics", "lang", "source"],
                user_fields=["id", "name", "username", "profile_image_url", "description"],
                expansions = ["author_id"]
            )
            if response.data:
                tweets.extend(response.data)
            if "next_token" in response.meta:
                next_token = response.meta["next_token"]
            else:
                next_token = None
            retries = 0
            time.sleep(1)
            if not next_token:
                break
        except tweepy.errors.TooManyRequests as e:
            retries += 1
            wait_time = (2 ** retries) + (random.randint(0, 1000) / 1000) #Exponential backoff with some random jitter
            print(f"Too many requests, waiting for {wait_time:.2f} seconds, retry {retries}/{max_retries}")
            time.sleep(wait_time)
        except Exception as e:
            print(f"An unexpected error has occurred: {e}")
            break
    return tweets, response.includes["users"] if response and isinstance(response, tweepy.Response) and 'users' in response.includes else []

if __name__ == '__main__':
    # Read bearer token from the config file
    try:
        with open("config.json", "r") as f:
            config = json.load(f) # read the file to a dictionary
            bearer_token = config["bearer_token"] # access the bearer_token field
    except FileNotFoundError:
        print("Error: config.json file not found")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in config.json")
        exit()
    except KeyError:
        print("Error: 'bearer_token' key not found in config.json")
        exit()
    # Example user ID (you can find the user ID by using the Twitter API or from the url of the user's profile page)
    user_id_1 = "2244994945" # TwitterDev
    #user_id_2 = "6253282" # Twitter # remove this user for testing purposes.

    user_ids = [user_id_1]  # Reduced to 1 user for testing

    for user_id in user_ids:
        tweets, users = get_all_tweets(user_id, bearer_token)
        for tweet in tweets:
            print(f"Tweet ID: {tweet.id}")
            print(f"Tweet Content: {tweet.text}")
            print(f"Tweet Created at: {tweet.created_at}")
            print(f"Tweet Language: {tweet.lang}")
            print(f"Tweet Likes: {tweet.public_metrics['like_count']}")
            print(f"Tweet Retweets: {tweet.public_metrics['retweet_count']}")
            print(f"Tweet Source: {tweet.source}")
            print("--------------------")
        for user in users:
            print(f"User ID: {user.id}")
            print(f"User Name: {user.name}")
            print(f"User Username: {user.username}")
            print(f"User Profile Image URL: {user.profile_image_url}")
            print(f"User Description: {user.description}")
            print("--------------------")