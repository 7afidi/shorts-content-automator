# Shorts Content Automator

Fully automated YouTube Shorts creation and publishing system. Generate content, create videos, and upload directly to YouTube with minimal human intervention.

## 🎬 Demo Channel

Check out the results of this automation tool in action:
[Daily Riddles YouTube Channel](https://www.youtube.com/@DailyRiddlesUs)

## ✨ Features

- Automated content generation using Claude AI
- Dynamic video creation with animations and text
- Text-to-speech narration
- Background music integration
- YouTube upload with AI-optimized metadata
- Complete end-to-end automation

## 🔄 Workflow

1. Content generation: Claude AI creates engaging content
2. Video generation: System creates animated frames with text and visuals
3. Audio creation: Text-to-speech narration with background music
4. Metadata optimization: Claude AI generates SEO-friendly titles, descriptions and tags
5. YouTube upload: Automatic publishing as Shorts

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/7afidi/shorts-content-automator.git
cd shorts-content-automator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Create a `.env` file in the project root with the following variables:
```
API_KEY=your_claude_api_key
YOUTUBE_CHANNEL_ID=your_channel_id
```

2. Set up YouTube API credentials:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create OAuth credentials
   - Download credentials as `client-secret.json` in project root

3. Create a `music` folder and add MP3 background tracks
4. Add an `icon.png` file to use as your channel logo/watermark

## 🚀 Usage

```bash
# Run the automation
python app.py
```

## 📁 Project Structure

- `app.py` - Main entry point
- `youtube_shorts_uploader.py` - YouTube API integration
- `advanced_riddle_generator.py` - Content generation

## ⚖️ License

This project is open source and available under the MIT License.