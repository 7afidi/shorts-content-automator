from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import imageio
import math
from math import sin, cos, pi
import colorsys
import time
import os
import random
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
from riddle_generator import RiddleGenerator
from scipy.io import wavfile
from youtube_shorts_uploader import YouTubeShortsUploader
from advanced_riddle_generator import AdvancedRiddleGenerator

def cleanup_video_files(output_path):
    """Delete video files if they exist"""
    files_to_delete = [
        output_path,
        f"final_{output_path}",
        f"final_final_{output_path}"
    ]
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Deleted {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

class EnhancedShortsGenerator:
    def __init__(self, api_key=None):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.base_background = self.create_gradient_background()
        self.font_paths = [
            "/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf",  # Linux path
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",  # Alternative Linux path
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # Mac path
            "C:/Windows/Fonts/arialbd.ttf",  # Windows path
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"  # Fallback font
        ]
        self.font_bold = self.get_available_font()
        self.icon_size = (320, 320)
        self.icon_pos = (self.width//2 - 160, 200)
        self.icon_img = self.load_icon()
        self.riddle_generator = AdvancedRiddleGenerator(api_key=api_key) if api_key else None
        
        self.header_pos = (self.width//2, 150)
        self.timer_pos = (self.width//2, 700)
        self.question_pos = (self.width//2, 900)
        self.answer_pos = (self.width//2, 1400)

    def get_available_font(self):
        """Try different font paths and return the first available one"""
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                print(f"Using font: {font_path}")
                return font_path
                
        # If no Arial found, try to find any available bold font
        try:
            import subprocess
            font_list = subprocess.check_output(['fc-list', ':style=Bold']).decode()
            if font_list:
                first_font = font_list.split('\n')[0].split(':')[0]
                print(f"Using alternative bold font: {first_font}")
                return first_font
        except:
            pass
            
        raise FileNotFoundError("No suitable bold font found. Please install ttf-mscorefonts-installer")
    
    def get_random_music(self):
        music_folder = "music"
        music_files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            return None
        chosen_music = random.choice(music_files)
        return os.path.join(music_folder, chosen_music)
    
    def validate_music_file(self, file_path):
        """Validate if the music file is properly formatted"""
        try:
            from moviepy.editor import AudioFileClip
            with AudioFileClip(file_path) as audio:
                duration = audio.duration
                return True if duration > 0 else False
        except Exception as e:
            print(f"Failed to validate music file {file_path}: {str(e)}")
            return False

    def create_silence(self, duration, output_path="silence.wav"):
        sample_rate = 44100
        audio_data = np.zeros(int(duration * sample_rate)).astype(np.int16)
        wavfile.write(output_path, sample_rate, audio_data)
        return output_path

    def load_icon(self):
        icon = Image.open('icon.png').convert('RGBA')
        return icon.resize(self.icon_size)

    def create_gradient_background(self):
        gradient = np.linspace(0, 1, self.height)
        purple = np.array([139, 92, 246])
        blue = np.array([37, 99, 235])
        gradient = gradient[:, np.newaxis, np.newaxis]
        arr = (gradient * purple + (1 - gradient) * blue).astype(np.uint8)
        return Image.fromarray(np.repeat(arr, self.width, axis=1))

    def draw_text_with_effects(self, draw, text, position, font_size, color):
        font = ImageFont.truetype(self.font_bold, font_size)
        x, y = position
        
        max_width = self.width - 100
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), line_text, font=font)
            if bbox[2] - bbox[0] > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(line_text)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = font_size * 1.2
        total_height = len(lines) * line_height
        start_y = y - (total_height / 2)
        
        for i, line in enumerate(lines):
            line_y = start_y + (i * line_height)
            draw.text((x + 5, line_y + 5), line, font=font, fill=(0, 0, 0, 150), anchor="mm")
            draw.text((x, line_y), line, font=font, fill=color, anchor="mm")

    def create_animated_timer(self, draw, time_remaining):
        self.draw_text_with_effects(draw, str(int(time_remaining)), 
                              self.timer_pos, 120, 'white')

    def generate_audio(self, text, output_path):
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        return AudioFileClip(output_path)

    def create_frame(self, questions, q_index, show_question=True, timer=None, answer_progress=0):
        frame = self.base_background.copy()
        draw = ImageDraw.Draw(frame)
        
        self.draw_text_with_effects(draw, "Daily Riddles", 
                                  self.header_pos, 72, 'white')
        frame.paste(self.icon_img, self.icon_pos, self.icon_img)
        
        if show_question:
            question = questions[q_index]["question"]
            self.draw_text_with_effects(draw, question, self.question_pos, 64, 'white')
        
        if answer_progress > 0:
            answer = questions[q_index]["answer"]
            chars_to_show = int(len(answer) * answer_progress)
            self.draw_text_with_effects(draw, answer[:chars_to_show], 
                                      self.answer_pos, 72, (255, 195, 0))
        
        if timer is not None:
            self.create_animated_timer(draw, timer)
            
        return np.array(frame)
    
    def generate_video(self, questions, output_path, audio_path=None):
        try:
            countdown_duration = 5
            answer_duration = 3
            question_delay = 2
            
            cleanup_video_files(output_path)
            
            writer = imageio.get_writer(output_path, fps=self.fps,
                                    codec='h264', quality=9,
                                    pixelformat='yuv420p',
                                    macro_block_size=8)
            
            audio_clips = []
            silence_path = self.create_silence(10)
            silence = AudioFileClip(silence_path)
            
            bg_music_path = self.get_random_music()
            if bg_music_path:
                bg_music = AudioFileClip(bg_music_path)
                bg_music = bg_music.volumex(0.05)
            
            start_time = time.time()
            
            question_clips = []
            answer_clips = []
            for q_index, question in enumerate(questions):
                q_audio_path = f"question_{q_index}.mp3"
                a_audio_path = f"answer_{q_index}.mp3"
                
                q_clip = self.generate_audio(question["question"], q_audio_path)
                a_clip = self.generate_audio(question["answer"], a_audio_path)
                
                question_clips.append(q_clip)
                answer_clips.append(a_clip)
            
            total_duration = 0
            
            for q_index, (q_clip, a_clip) in enumerate(zip(question_clips, answer_clips)):
                question_duration = q_clip.duration
                
                blank_frame = self.create_frame(questions, q_index, show_question=False)
                blank_duration = 0.5
                for _ in range(int(blank_duration * self.fps)):
                    writer.append_data(blank_frame)
                audio_clips.append(silence.subclip(0, blank_duration))
                total_duration += blank_duration
                
                question_frame = self.create_frame(questions, q_index)
                for _ in range(int(question_duration * self.fps)):
                    writer.append_data(question_frame)
                audio_clips.append(q_clip)
                total_duration += question_duration
                
                pause_duration = 1
                for _ in range(int(pause_duration * self.fps)):
                    writer.append_data(question_frame)
                audio_clips.append(silence.subclip(0, pause_duration))
                total_duration += pause_duration
                
                countdown_silence = silence.subclip(0, countdown_duration)
                for t in np.linspace(countdown_duration, 0, countdown_duration*self.fps, endpoint=False):
                    frame = self.create_frame(questions, q_index, timer=math.ceil(t))
                    writer.append_data(frame)
                audio_clips.append(countdown_silence)
                total_duration += countdown_duration
                
                answer_frames = int(max(answer_duration, a_clip.duration) * self.fps)
                for p in np.linspace(0, 1, answer_frames):
                    frame = self.create_frame(questions, q_index, answer_progress=p)
                    writer.append_data(frame)
                audio_clips.append(a_clip)
                total_duration += max(answer_duration, a_clip.duration)
                
                if a_clip.duration < answer_duration:
                    silence_duration = answer_duration - a_clip.duration
                    audio_clips.append(silence.subclip(0, silence_duration))
                    total_duration += silence_duration
                
                if q_index < len(questions) - 1:
                    last_frame = self.create_frame(questions, q_index, answer_progress=1)
                    for _ in range(question_delay * self.fps):
                        writer.append_data(last_frame)
                    audio_clips.append(silence.subclip(0, question_delay))
                    total_duration += question_delay
                
                elapsed = time.time() - start_time
                progress = (q_index + 1) / len(questions) * 100
                print(f"Progress: {progress:.1f}% | Time elapsed: {elapsed:.1f}s")
            
            writer.close()
            
            final_voice = concatenate_audioclips(audio_clips)
            
            if bg_music_path:
                if bg_music.duration < total_duration:
                    num_loops = math.ceil(total_duration / bg_music.duration)
                    bg_music = concatenate_audioclips([bg_music] * num_loops)
                bg_music = bg_music.subclip(0, total_duration)
                final_audio = CompositeAudioClip([bg_music, final_voice])
            else:
                final_audio = final_voice
            
            video = VideoFileClip(output_path)
            final_video = video.set_audio(final_audio)
            final_video.write_videofile(f"final_{output_path}", codec='libx264', audio_codec='aac')
            
            video.close()
            final_audio.close()
            if bg_music_path:
                bg_music.close()
            for clip in audio_clips:
                if isinstance(clip, AudioFileClip):
                    clip.close()
            for i in range(len(questions)):
                os.remove(f"question_{i}.mp3")
                os.remove(f"answer_{i}.mp3")
            os.remove(silence_path)
                
            print(f"Video saved to final_{output_path} in {time.time()-start_time:.1f} seconds")
            return True
            
        except Exception as e:
            print(f"Error generating video: {e}")
            cleanup_video_files(output_path)
            return False


if __name__ == "__main__":
    # Replace with your API key or load from environment variables
    api_key = os.environ.get("RIDDLE_API_KEY", "")  
    generator = EnhancedShortsGenerator(api_key=api_key)
    
    # Initialize the uploader with your credentials
    uploader = YouTubeShortsUploader(
        client_secrets_file='client-secret.json',  # Path to your OAuth client secrets file
        target_channel_id=os.environ.get("YOUTUBE_CHANNEL_ID", ""),
        api_key=api_key
    )
    
    print("Generating riddles...")
    riddle_generator = AdvancedRiddleGenerator(api_key=api_key)
    riddles = riddle_generator.generate_riddles()
    
    if riddles:
        output_path = "puzzle_shorts.mp4"
        print("Generating video...")
        
        if generator.generate_video(questions=riddles, output_path=output_path):
            print("Uploading to YouTube...")
            riddle_content = " | ".join([f"Q: {r['question']} A: {r['answer']}" for r in riddles])
            video_id = uploader.upload_short(f"final_{output_path}", riddle_content)
            
            if video_id:
                print(f"Successfully uploaded! Video ID: {video_id}")
                cleanup_video_files(output_path)
            else:
                print("Upload failed.")
                cleanup_video_files(output_path)
        else:
            print("Video generation failed.")
    else:
        print("Failed to generate riddles")