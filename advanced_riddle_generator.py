from openai import OpenAI
import json
from riddle_history import RiddleHistory
import random
from datetime import datetime
from claude_client import ClaudeClient

class AdvancedRiddleGenerator:
    def __init__(self, api_key):
        self.client = ClaudeClient(
            api_key=api_key,
            site_name="RiddleGenerator"
        )
        self.history = RiddleHistory()
        
        self.categories = [
            "nature", "food", "technology", "space", "animals", "sports",
            "music", "art", "science", "geography", "history", "mathematics",
            "literature", "movies", "careers", "transportation", "weather",
            "ocean", "buildings", "clothing", "emotions", "time", "colors",
            "seasons", "household", "body", "language", "celebrations"
        ]
        
        self.complexity_levels = ["easy", "medium", "hard"]
        self.riddle_types = [
            "wordplay", "metaphor", "observation", "process", "paradox",
            "mathematical", "logical", "what-am-i", "sequence", "transformation"
        ]

    def _get_theme_rotation(self):
        """Get theme combination based on current date to ensure variety"""
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        
        category = self.categories[day_of_year % len(self.categories)]
        complexity = self.complexity_levels[(day_of_year // 3) % len(self.complexity_levels)]
        riddle_type = self.riddle_types[(day_of_year // 2) % len(self.riddle_types)]
        
        return category, complexity, riddle_type

    def _generate_riddle_batch(self, count, attempt=1):
        category, complexity, riddle_type = self._get_theme_rotation()
        
        prompt = f"""Generate {count} unique, creative riddles about {category} using {riddle_type} style at {complexity} difficulty.
        
        STRICT LENGTH REQUIREMENTS:
        - Questions must be 10-15 words maximum
        - Answers must be 8-12 words maximum
        - No multi-part questions or answers
        - Keep everything on a single line
        
        Guidelines:
        - Theme: Focus on {category}-related concepts
        - Style: Use {riddle_type} approach
        - Difficulty: Keep it {complexity} level
        - Format: JSON array with 'question' and 'answer' fields
        - Must be completely original riddles (attempt {attempt})
        
        Additional requirements:
        - Include brief, focused learning elements in answers
        - Avoid common riddles
        - Keep language simple and clear
        - Ensure cultural neutrality
        - Perfect for social media

        Return the response in this exact JSON format:
        [
            {{"question": "Your riddle question here", "answer": "Your riddle answer here"}},
            {{"question": "Second riddle question", "answer": "Second riddle answer"}},
            ...
        ]
        """
        
        response = self.client.prompt(message=prompt)
        
        if response["status"] == "error":
            print(f"Error from API: {response.get('error')}")
            return None
            
        if not response["message"]:
            print("No message in response")
            return None
            
        try:
            print(f"Attempting to parse JSON response: {response['message'][:200]}...")  # Print first 200 chars for debugging
            riddles = json.loads(response['message'])
            valid_riddles = []
            
            if not isinstance(riddles, list):
                print(f"Expected list but got {type(riddles)}")
                return None
                
            for riddle in riddles:
                if not isinstance(riddle, dict) or 'question' not in riddle or 'answer' not in riddle:
                    print(f"Invalid riddle format: {riddle}")
                    continue
                    
                question_words = len(riddle['question'].split())
                answer_words = len(riddle['answer'].split())
                
                if (10 <= question_words <= 15 and 
                    8 <= answer_words <= 12 and 
                    '\n' not in riddle['question'] and 
                    '\n' not in riddle['answer']):
                    
                    riddle['metadata'] = {
                        'category': category,
                        'complexity': complexity,
                        'type': riddle_type,
                        'generated_date': datetime.now().isoformat(),
                        'question_words': question_words,
                        'answer_words': answer_words
                    }
                    valid_riddles.append(riddle)
                    
            return valid_riddles
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Raw response: {response['message']}")
            return None

    def generate_riddles(self, count=3, max_attempts=3):
        """Generate unique riddles with theme rotation and length constraints"""
        unique_riddles = []
        attempts = 0
        
        while len(unique_riddles) < count and attempts < max_attempts:
            print(f"\nAttempt {attempts + 1} to generate {count - len(unique_riddles)} unique riddles...")
            
            batch_size = (count - len(unique_riddles)) * 2
            riddles = self._generate_riddle_batch(batch_size, attempts + 1)
            
            if riddles:
                for riddle in riddles:
                    if not self.history.is_riddle_used(riddle):
                        unique_riddles.append(riddle)
                        print(f"✓ New unique riddle ({riddle['metadata']['category']}/{riddle['metadata']['type']})")
                        print(f"  Question: {len(riddle['question'].split())} words")
                        print(f"  Answer: {len(riddle['answer'].split())} words")
                        if len(unique_riddles) >= count:
                            break
                    else:
                        print(f"✗ Duplicate found, skipping...")
            
            if len(unique_riddles) < count:
                print(f"Need {count - len(unique_riddles)} more riddles...")
            
            attempts += 1
        
        if unique_riddles:
            self.history.add_riddles(unique_riddles)
            total_riddles = self.history.get_riddle_count()
            print(f"\nSuccess! Total unique riddles in history: {total_riddles}")
            
        return unique_riddles[:count] if unique_riddles else None