import json
import os
import random
from datetime import datetime

class Word:
    """Represents a vocabulary word with learning status"""
    def __init__(self, word, definition, status="not_learned", attempts=0, correct=0, wrong=0):
        self.word = word.strip().lower()  # Format: lowercase, no leading/trailing spaces
        self.definition = definition.strip()
        self.status = status  # "not_learned", "few_mistakes", "learned"
        self.attempts = attempts
        self.correct = correct
        self.wrong = wrong
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "word": self.word,
            "definition": self.definition,
            "status": self.status,
            "attempts": self.attempts,
            "correct": self.correct,
            "wrong": self.wrong
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Word object from dictionary"""
        return cls(
            word=data["word"],
            definition=data["definition"],
            status=data.get("status", "not_learned"),
            attempts=data.get("attempts", 0),
            correct=data.get("correct", 0),
            wrong=data.get("wrong", 0)
        )
    
    def update_status(self, guessed_correctly, attempts_used):
        """
        Update word status based on game result
        - First time correct (1 attempt) = "learned"
        - First time wrong (2-3 attempts) = "few_mistakes"
        - Failed all 3 attempts = "not_learned"
        """
        self.attempts += 1
        
        if guessed_correctly:
            self.correct += 1
            if attempts_used == 1:
                # Got it on first try
                self.status = "learned"
            else:
                # Needed multiple tries
                self.status = "few_mistakes"
        else:
            # Failed all attempts
            self.wrong += 1
            self.status = "not_learned"
    
    def get_display_length(self):
        """Get word length including spaces and hyphens"""
        return len(self.word)
    
    def get_grid_word(self):
        """Get word with spaces and hyphens preserved for gameplay"""
        return self.word.upper()


class DataManager:
    """Manages vocabulary word storage and retrieval"""
    def __init__(self, filepath="data/vocabulary.json"):
        self.filepath = filepath
        self.words = []
        self.ensure_data_directory()
        self.load_words()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def load_words(self):
        """Load words from JSON file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.words = [Word.from_dict(w) for w in data.get("words", [])]
                print(f"✓ Loaded {len(self.words)} words from {self.filepath}")
            except Exception as e:
                print(f"✗ Error loading words: {e}")
                self.words = []
        else:
            print(f"⚠ No vocabulary file found. Starting fresh.")
            self.words = []
            self.save_words()  # Create empty file
    
    def save_words(self):
        """Save words to JSON file"""
        try:
            data = {
                "words": [word.to_dict() for word in self.words]
            }
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.words)} words to {self.filepath}")
            return True
        except Exception as e:
            print(f"✗ Error saving words: {e}")
            return False
    
    def add_word(self, word_text, definition):
        """
        Add a new word with validation
        Returns: (success: bool, message: str)
        """
        # Format and validate
        word_text = word_text.strip().lower()
        definition = definition.strip()
        
        # Validation checks
        if not word_text:
            return False, "Word cannot be empty"
        
        if not definition:
            return False, "Definition cannot be empty"
        
        if len(word_text) > 20:
            return False, "Word must be 20 characters or less"
        
        
        
        # Check for duplicates
        if self.word_exists(word_text):
            # Add word
            new_word = Word(word_text, definition)
            self.words.append(new_word)
            self.save_words()
            return True, f"Word '{word_text}' already exists, you could delete if duplicate"
        
        # Add word
        new_word = Word(word_text, definition)
        self.words.append(new_word)
        self.save_words()
        
        return True, f"Added '{word_text}' successfully!"
    
    def word_exists(self, word_text):
        """Check if word already exists"""
        word_text = word_text.strip().lower()
        return any(w.word == word_text for w in self.words)
    
    def get_word(self, word_text):
        """Get a specific word object"""
        word_text = word_text.strip().lower()
        for word in self.words:
            if word.word == word_text:
                return word
        return None
    
    def delete_word(self, word_text):
        """Delete a word"""
        word_text = word_text.strip().lower()
        self.words = [w for w in self.words if w.word != word_text]
        self.save_words()
        return True
    
    def update_word_status(self, word_text, guessed_correctly, attempts_used):
        """Update word status after gameplay"""
        word = self.get_word(word_text)
        if word:
            word.update_status(guessed_correctly, attempts_used)
            self.save_words()
            return True
        return False
    
    def get_all_words(self, sort_by="alphabetical", filter_status=None):
        """
        Get all words with optional sorting and filtering
        sort_by: "alphabetical", "status", "attempts"
        filter_status: None, "not_learned", "few_mistakes", "learned"
        """
        filtered_words = self.words
        
        # Filter by status
        if filter_status:
            filtered_words = [w for w in filtered_words if w.status == filter_status]
        
        # Sort
        if sort_by == "alphabetical":
            filtered_words = sorted(filtered_words, key=lambda w: w.word)
        elif sort_by == "status":
            status_order = {"not_learned": 0, "few_mistakes": 1, "learned": 2}
            filtered_words = sorted(filtered_words, key=lambda w: status_order.get(w.status, 0))
        elif sort_by == "attempts":
            filtered_words = sorted(filtered_words, key=lambda w: w.attempts, reverse=True)
        
        return filtered_words
    
    def get_random_word_weighted(self):
        if not self.words:
            return None
        
        # Group words by status
        not_learned = [w for w in self.words if w.status == "not_learned"]
        few_mistakes = [w for w in self.words if w.status == "few_mistakes"]
        learned = [w for w in self.words if w.status == "learned"]
        
        # Create weighted pool
        weighted_pool = (
            not_learned * 70 +  # 70% weight
            few_mistakes * 25 +  # 30% weight
            learned * 5         # 20% weight
        )
        
        if not weighted_pool:
            # Fallback to random if no words match
            return random.choice(self.words)
        
        return random.choice(weighted_pool)
    
    def get_statistics(self):
        """Get learning statistics"""
        if not self.words:
            return {
                "total": 0,
                "not_learned": 0,
                "few_mistakes": 0,
                "learned": 0,
                "percent_learned": 0
            }
        
        stats = {
            "total": len(self.words),
            "not_learned": len([w for w in self.words if w.status == "not_learned"]),
            "few_mistakes": len([w for w in self.words if w.status == "few_mistakes"]),
            "learned": len([w for w in self.words if w.status == "learned"]),
        }
        stats["percent_learned"] = int((stats["learned"] / stats["total"]) * 100)
        
        return stats

