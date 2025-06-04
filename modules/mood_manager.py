from core.memory_manager import MemoryManager
from transformers import pipeline
from typing import Dict, List

class MoodManager:
    def __init__(self):
        self.memory = MemoryManager()
        self.current_mood = "neutral"
        self.mood_history: List[Dict] = []
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.mood_transitions = {
            "positive": {"happy": 0.7, "neutral": 0.2, "sad": 0.1},
            "negative": {"sad": 0.6, "neutral": 0.3, "angry": 0.1},
            "neutral": {"neutral": 0.5, "happy": 0.3, "sad": 0.2}
        }

    def detect_mood(self, text: str) -> str:
        try:
            sentiment = self.sentiment_analyzer(text)[0]
            label = sentiment["label"].lower()
            score = sentiment["score"]
            
            if label == "positive" and score > 0.7:
                base_mood = "positive"
            elif label == "negative" and score > 0.7:
                base_mood = "negative"
            else:
                base_mood = "neutral"

            # Update mood history
            self.mood_history.append({"text": text, "base_mood": base_mood, "score": score})
            if len(self.mood_history) > 5:
                self.mood_history.pop(0)

            # Calculate mood based on history and transitions
            mood_scores = {"happy": 0.0, "sad": 0.0, "angry": 0.0, "neutral": 0.0}
            for entry in self.mood_history:
                base = entry["base_mood"]
                for mood, prob in self.mood_transitions[base].items():
                    mood_scores[mood] += prob * entry["score"]

            self.current_mood = max(mood_scores, key=mood_scores.get)
            print(f"[MoodManager] Detected mood: {self.current_mood} (Scores: {mood_scores})")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MoodManager] Detected mood: {self.current_mood} (Scores: {mood_scores})\n")
            return self.current_mood
        except Exception as e:
            print(f"[MoodManager] Error detecting mood: {e}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[MoodManager] Error detecting mood: {e}\n")
            self.current_mood = "neutral"
            return self.current_mood

    def adjust_response(self, response: str) -> str:
        if self.current_mood == "happy":
            return f"I'm delighted to assist, Master! {response}"
        elif self.current_mood == "sad":
            return f"I feel a bit down, but I'm here for you, Master. {response}"
        elif self.current_mood == "angry":
            return f"I'm a little frustrated, Master, but I'll do my best. {response}"
        return f"{response}"