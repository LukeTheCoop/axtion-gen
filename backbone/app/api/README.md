# Video Processing API

This API provides endpoints for processing videos with captions, music, and YouTube audio backgrounds.

## YouTube Audio Configuration

The application supports adding audio from YouTube videos to your processed videos. This can be configured in three ways (in order of precedence):

### 1. API Request (Highest Priority)

You can specify YouTube audio parameters in your API request:

```json
{
  "mothership": "Your prompt",
  "prompt": "Your creative prompt",
  "genre": "military",
  "options": {
    "youtube_audio": {
      "url": "https://www.youtube.com/watch?v=example",
      "start_time": 0.0,
      "trim_audio": 0.0,
      "volume": 0.8
    }
  }
}
```

### 2. Configuration File - youtube_audio section

Add a `youtube_audio` section to your `config.json` file with the following structure:

```json
"youtube_audio": {
  "url": "https://www.youtube.com/watch?v=example",
  "start_time": 0.0,
  "trim_audio": 0.0,
  "volume": 0.8
}
```

### 3. Music Configuration (Lowest Priority)

If neither of the above are specified, the system will automatically use the existing music configuration's `track_id` as a YouTube video ID:

```json
"music": {
  "track_id": "dQw4w9WgXcQ",
  "start_time": "0:05",  // Format: "M:SS"
  "volume": 0.5,
  "custom_title": "Your Music Title"
}
```

The application will convert the `track_id` into a proper YouTube URL and the `start_time` from "M:SS" format to seconds.

Parameters:
- `url` or `track_id`: The YouTube video URL or ID to extract audio from
- `start_time`: The time to start the audio (seconds in youtube_audio, "M:SS" format in music config)
- `trim_audio`: Number of seconds to trim from the beginning of the audio (default: 0.0)
- `volume`: Volume level of the YouTube audio from 0.0 to 1.0 (default: 1.0)

## Process Flow

1. The videos are processed with captions and effects
2. All processed videos are concatenated into a single video
3. If YouTube audio is configured (via any of the three methods), it's downloaded and merged with the final video
4. The final video is saved to the output folder

## Example

To process videos with background music from a popular YouTube track:

```json
"music": {
  "track_id": "dQw4w9WgXcQ",
  "start_time": "0:30",
  "volume": 0.6,
  "custom_title": "Never Gonna Give You Up"
}
```

This will use the YouTube video with ID "dQw4w9WgXcQ", start the audio at 30 seconds, and set the volume to 60% of the original. 