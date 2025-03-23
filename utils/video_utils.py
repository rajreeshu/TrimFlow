import re
import requests
from fastapi import File, HTTPException, UploadFile
from pytube import YouTube
from instaloader import Instaloader, Post
import tweepy
import io
import yt_dlp
import os

def download_youtube_video_with_ytdlp(youtube_url):
    """Download a YouTube video using yt-dlp"""
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
            'outtmpl':'%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)

            # Get the content type based on file extension
            ext = os.path.splitext(filename)[1].lstrip('.')
            content_type = f"video/{ext}" if ext != 'webm' else "video/webm"

            # Open the file and read its contents into memory
            with open(filename, 'rb') as f:
                file_content = f.read()

            # Create a SpooledTemporaryFile for the UploadFile
            spooled_file = io.BytesIO(file_content)

            # Create an UploadFile object
            upload_file = UploadFile(
                filename=os.path.basename(filename),
                file=spooled_file,
            )

            # Clean up the temporary file
            try:
                os.remove(filename)
            except:
                pass

            return upload_file

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def download_video_from_instagram(url: str) -> File:
    loader = Instaloader()
    post = Post.from_shortcode(loader.context, url.split('/')[-2])
    file_path = loader.download_post(post, target='.')
    return open(file_path, 'rb')

def download_video_from_twitter(url: str) -> File:

    # Set up tweepy with your credentials
    consumer_key = 'your_consumer_key'
    consumer_secret = 'your_consumer_secret'
    access_token = 'your_access_token'
    access_token_secret = 'your_access_token_secret'

    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    tweet_id = url.split('/')[-1]
    tweet = api.get_status(tweet_id, tweet_mode='extended')
    media = tweet.extended_entities['media'][0]
    video_url = media['video_info']['variants'][0]['url']

    response = requests.get(video_url)
    file_path = 'twitter_video.mp4'
    with open(file_path, 'wb') as f:
        f.write(response.content)

    return open(file_path, 'rb')


def download_online_video_from_direct_url(url: str) -> UploadFile:
    response = requests.get(url)
    if response.status_code == 200:
        file_extension = os.path.splitext(url)[1]
        file_path = 'downloaded_video' + file_extension
        with open(file_path, 'wb') as f:
            f.write(response.content)

        # Read the file content into memory
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Create a SpooledTemporaryFile for the UploadFile
        spooled_file = io.BytesIO(file_content)

        # Create an UploadFile object
        upload_file = UploadFile(
            filename=os.path.basename(file_path),
            file=spooled_file,
        )

        # Clean up the temporary file
        try:
            os.remove(file_path)
        except:
            pass

        return upload_file
    else:
        raise HTTPException(status_code=400, detail="Failed to download video")

def download_online_video(url: str) -> File:
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    instagram_pattern = re.compile(r'(https?://)?(www\.)?instagram\.com/.+')
    twitter_pattern = re.compile(r'(https?://)?(www\.)?(twitter|x)\.com/.+')
    direct_video_pattern = re.compile(r'.*\.(mp4|avi|mov|mkv|webm)$')

    if youtube_pattern.match(url):
        return download_youtube_video_with_ytdlp(url)
    elif instagram_pattern.match(url):
        return download_video_from_instagram(url)
    elif twitter_pattern.match(url):
        return download_video_from_twitter(url)
    elif direct_video_pattern.match(url):
        return download_online_video_from_direct_url(url)
    else:
        raise ValueError("Unsupported URL")