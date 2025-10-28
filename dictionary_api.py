import requests
import random

def get_random_word():
    """Get a random English word."""
    try:
        res = requests.get("https://random-word-api.herokuapp.com/word?lang=en")
        if res.status_code == 200:
            word = res.json()[0]
            # Filter out very long words (max 20 chars)
            if len(word) <= 20:
                return word.lower()
    except Exception as e:
        print("Random word API error:", e)
    return None

def get_definition(word):
    """Get definition from dictionaryapi.dev"""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            meanings = data[0].get("meanings", [])
            if meanings:
                defs = meanings[0].get("definitions", [])
                if defs:
                    return defs[0].get("definition")
    except Exception as e:
        print("Definition API error:", e)
    return None

def get_random_word_with_definition(max_attempts=10):
    """
    Get a random word with its definition.
    Tries multiple times if definition is not found.
    Returns: (word, definition) tuple or (None, None)
    """
    for attempt in range(max_attempts):
        word = get_random_word()
        if word:
            print(f"Trying word: {word}...")
            definition = get_definition(word)
            if definition:
                print(f"✓ Found: {word} - {definition[:50]}...")
                return word, definition
            else:
                print(f"✗ No definition for: {word}")
    
    print("Failed to get word after maximum attempts")
    return None, None

# Fallback word list (in case API fails)
FALLBACK_WORDS = [
    ("apple", "A round fruit with red or green skin and crisp flesh"),
    ("book", "A written or printed work consisting of pages"),
    ("chair", "A separate seat for one person, with a back and four legs"),
    ("dance", "Move rhythmically to music"),
    ("energy", "The strength and vitality required for sustained activity"),
    ("friend", "A person with whom one has a bond of mutual affection"),
    ("garden", "A piece of ground for growing flowers, fruit, or vegetables"),
    ("house", "A building for human habitation"),
    ("island", "A piece of land surrounded by water"),
    ("jungle", "An area of land overgrown with dense vegetation"),
]

def get_fallback_word():
    """Get a random word from fallback list"""
    return random.choice(FALLBACK_WORDS)

# Test function
if __name__ == "__main__":
    print("Testing Infinity Mode API...")
    word, definition = get_random_word_with_definition(max_attempts=5)
    if word and definition:
        print(f"\n✓ Success!")
        print(f"Word: {word}")
        print(f"Definition: {definition}")
    else:
        print("\n✗ Failed, using fallback")
        word, definition = get_fallback_word()
        print(f"Word: {word}")
        print(f"Definition: {definition}")