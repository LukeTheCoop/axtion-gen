import os
import json

def update_video_list():
    # Path to the directory containing the videos
    video_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the JSON file
    json_file = os.path.join(video_dir, "video_list.json")
    
    # Get all MP4 files in the directory
    video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
    
    # Sort the files alphabetically
    video_files.sort()
    
    # Write the list to the JSON file
    with open(json_file, 'w') as f:
        json.dump(video_files, f, indent=4)
    
    print(f"Updated {json_file} with {len(video_files)} videos")

if __name__ == "__main__":
    update_video_list()
