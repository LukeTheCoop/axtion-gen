import requests
import json
import datetime
import socket
import platform
import uuid
import os
import mimetypes
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Cloudinary API secret from environment variables
CLOUD_API_SECRET = os.getenv('CLOUD')
if not CLOUD_API_SECRET:
    print("Warning: CLOUD environment variable not found. Using default configuration.")

# Cloudinary configuration
# Already set with your credentials
cloudinary.config(
    cloud_name = "ddab3rxhe",
    api_key = "942222813488427",
    api_secret = CLOUD_API_SECRET
)

# Rate limiter class to manage webhook request timing
class RateLimiter:
    def __init__(self, interval_seconds=10):
        self.interval_seconds = interval_seconds
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to maintain the minimum interval between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.interval_seconds and self.last_request_time > 0:
            wait_time = self.interval_seconds - time_since_last_request
            print(f"\nRate limiting: Waiting {wait_time:.2f} seconds before next request...")
            time.sleep(wait_time)
        
        # Always update the last request time after checking (fixed)
        self.last_request_time = time.time()

# Create a global rate limiter instance
rate_limiter = RateLimiter(interval_seconds=10)

def upload_to_cloudinary(video_path):
    """Upload a video to Cloudinary and return the URL."""
    try:
        # Check if the video file exists
        if not os.path.exists(video_path):
            return {"error": f"Video file not found: {video_path}"}
        
        # Upload the video to Cloudinary
        print("Uploading video to Cloudinary...")
        result = cloudinary.uploader.upload(
            video_path,
            resource_type="video",
            folder="webhook_videos"
        )
        
        # Get URLs from the result
        video_url = result['secure_url']
        thumbnail_url = cloudinary.utils.cloudinary_url(
            result['public_id'], 
            format='jpg', 
            resource_type='video', 
            width=320, 
            height=240, 
            crop='fill'
        )[0]
        
        return {
            "success": True,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "public_id": result['public_id'],
            "format": result['format'],
            "version": result['version']
        }
    except Exception as e:
        print(f"Cloudinary upload error: {str(e)}")
        return {"error": str(e)}

def get_video_cloudinary(video_path="input_video.mp4", title="Axtion Entertainment", caption="Axtion Entertainment is a company that makes videos"):
    """Upload video to Cloudinary and prepare HTML video element with Cloudinary URL."""
    try:
        # Check if the video file exists
        if not os.path.exists(video_path):
            return {"error": f"Video file not found: {video_path}"}
        
        # Get file size information
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Upload to Cloudinary
        cloudinary_result = upload_to_cloudinary(video_path)
        
        # Check for upload errors
        if "error" in cloudinary_result:
            return {"error": f"Cloudinary upload failed: {cloudinary_result['error']}"}
        
        # Get the video URL from Cloudinary
        video_url = cloudinary_result["video_url"]
        thumbnail_url = cloudinary_result["thumbnail_url"]
        
        # Create HTML video tag with Cloudinary URL
        video_html = f"""
        <video width="640" height="360" controls poster="{thumbnail_url}">
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        """
        
        data = {
            "processed": "no",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sent_from": {
                "hostname": socket.gethostname(),
                "os_name": platform.system(),
                "os_version": platform.release(),
                "device_id": str(uuid.getnode()),
                "username": os.getlogin()
            },
            "video_info": {
                "file_name": os.path.basename(video_path),
                "file_size_mb": file_size_mb,
                "title": title,
                "caption": caption,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "video_html": video_html,
                "cloudinary_details": cloudinary_result
            }
        }
        
        return data
    except Exception as e:
        print(f"Error in get_video_cloudinary: {str(e)}")
        return {"error": str(e)}

def send_to_webhook(data):
    """Send the collected data to the Make.com webhook."""
    # Use the rate limiter to enforce minimum time between requests
    rate_limiter.wait_if_needed()
    
    webhook_url = "https://hook.us2.make.com/9t5shtmztpifk18q3o9qfjjq6mqnxseb"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to webhook at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    print(f"Using webhook URL: {webhook_url}")
    
    try:
        # Add timeout to prevent hanging
        response = requests.post(webhook_url, headers=headers, data=json.dumps(data), timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return {
            "status_code": response.status_code,
            "response": response.text
        }
    except requests.exceptions.Timeout:
        print("Webhook request timed out after 30 seconds")
        return {"error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        print("Connection error when sending to webhook - check your internet connection")
        return {"error": "Connection error"}
    except Exception as e:
        print(f"Error in send_to_webhook: {str(e)}")
        return {"error": str(e)}

def process_video(video_path, title, caption):
    """Process a single video and send it to the webhook."""
    print(f"\nProcessing video: {video_path} with title: {title}")
    
    # Validate file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    print(f"File exists and is {os.path.getsize(video_path) / (1024 * 1024):.2f} MB")
    
    video_info = get_video_cloudinary(video_path, title, caption)
    
    if "error" in video_info:
        print(f"Error processing video: {video_info['error']}")
        return False
    
    print("Sending data to Make.com webhook...")
    webhook_response = send_to_webhook(video_info)
    
    if "error" in webhook_response:
        print(f"Error sending data: {webhook_response['error']}")
        return False
    elif webhook_response.get("status_code") != 200:
        print(f"Webhook returned non-200 status code: {webhook_response.get('status_code')}")
        print(f"Response: {webhook_response.get('response')}")
        return False
    else:
        print(f"Data sent successfully! Response code: {webhook_response['status_code']}")
        print("The video information should now be available in your Google Sheet.")
    
    print("\nSent the following data (URLs truncated for display):")
    # Create a copy of the data for display
    display_data = json.loads(json.dumps(video_info))
    if "video_url" in display_data.get("video_info", {}):
        display_data["video_info"]["video_url"] = display_data["video_info"]["video_url"][:50] + "... [truncated]"
    if "thumbnail_url" in display_data.get("video_info", {}):
        display_data["video_info"]["thumbnail_url"] = display_data["video_info"]["thumbnail_url"][:50] + "... [truncated]"
    if "video_html" in display_data.get("video_info", {}):
        display_data["video_info"]["video_html"] = "[HTML VIDEO TAG]"
    print(json.dumps(display_data, indent=2))
    
    # Save HTML preview locally for testing

    return True

def process_upload_folder():
    """Process videos from the upload folder with user input for title and caption."""
    # Create upload folder if it doesn't exist
    upload_folder = "upload"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder: {upload_folder}")
        print("Please place video files in the upload folder and run this function again.")
        return
    
    # Get list of video files in the upload folder
    video_files = []
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            video_files.append(file_path)
    
    if not video_files:
        print(f"No video files found in {upload_folder} folder.")
        print("Please add video files (.mp4, .mov, .avi, .mkv) to the upload folder.")
        return
    
    print(f"Found {len(video_files)} video(s) in the upload folder.")
    
    # Process each video
    for video_path in video_files:
        print(f"\nPreparing to process: {video_path}")
        
        # Get title and caption from user input
        title = input(f"Enter title for {os.path.basename(video_path)} (default: Axtion Entertainment): ")
        if not title.strip():
            title = "Axtion Entertainment"
        
        caption = input(f"Enter caption (default: Axtion Entertainment is a cutting-edge media company): ")
        if not caption.strip():
            caption = "Axtion Entertainment is a cutting-edge media company specializing in immersive video experiences"
        
        # Process the video
        print(f"Processing {os.path.basename(video_path)}...")
        result = process_video(video_path, title, caption)
        
        if result is False:
            print(f"Failed to process {video_path}")
        else:
            print(f"Successfully processed {video_path}")
        
        # Ask if user wants to continue to the next video
        if video_files.index(video_path) < len(video_files) - 1:
            continue_input = input("\nProcess next video? (y/n): ").lower()
            if continue_input != 'y':
                print("Stopping video processing.")
                break

def main():
    """Main function to process video and send to webhook."""
    parser = argparse.ArgumentParser(description='Process a video and send it to a webhook with rate limiting.')
    parser.add_argument('--video', type=str, default='input_video.mp4', help='Path to the video file')
    parser.add_argument('--title', type=str, default='Axtion Entertainment', help='Title for the video')
    parser.add_argument('--caption', type=str, default='Axtion Entertainment is a cutting-edge media company specializing in immersive video experiences', help='Caption for the video')
    parser.add_argument('--count', type=int, default=1, help='Number of times to send the request (for testing rate limiting)')
    parser.add_argument('--test-webhook', action='store_true', help='Test the webhook directly without uploading a video')
    args = parser.parse_args()
    
    # Check if Cloudinary credentials are properly set
    if (cloudinary.config().cloud_name == "your_cloud_name" or
        cloudinary.config().api_key == "your_api_key" or
        cloudinary.config().api_secret == "your_api_secret"):
        print("ERROR: Please set your Cloudinary credentials in the script.")
        print("Replace 'your_cloud_name', 'your_api_key', and 'your_api_secret' with your actual Cloudinary credentials.")
        return
    
    
    # Send multiple requests if requested (for testing rate limiting)
    for i in range(args.count):
        if args.count > 1:
            print(f"\n=== Processing request {i+1} of {args.count} ===")
            # Create a unique title for each request in batch mode
            current_title = f"{args.title} - Batch {i+1}"
            preview_filename = f"video_preview_{i+1}.html"
        else:
            current_title = args.title
            preview_filename = "video_preview_cloudinary.html"
        
        success = process_video(args.video, current_title, args.caption, preview_filename)
        
        if not success:
            print(f"Failed to process request {i+1}. Stopping batch.")
            break
        
        if i < args.count - 1:
            print(f"\nCompleted request {i+1} of {args.count}")

if __name__ == "__main__":
    process_upload_folder()
