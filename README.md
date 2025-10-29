# Purrdle: A Cat-Themed Wordle Clone

## Overview

Purrdle is an innovative vocabulary learning application that combines the engaging gameplay mechanics of word-guessing puzzles with effective spaced repetition learning techniques. Built using Python and the Pygame library, the application transforms vocabulary acquisition from a mundane task into an entertaining and rewarding experience.

This project was created as part of **[Computational Thinking/CSC0014]**.  
It features a complete, playable game loop, a themed graphical interface, animations, and sound effects.

Video demo: [Youtube](https://youtu.be/_b8yhJW1820)

---
## Requirements

- **Python 3.8+**  
- **Pygame** (see `requirements.txt`)
- **Request** (for calling API)

---

## Installation & Setup

### Step 1: Download the source code

Clone or download the source code from this repository:

```bash
git clone https://github.com/htham-eituc/Purrdle_Vocab_Learn
cd Purrdle
```

---

### Step 2: Place the `assets/` Folder

(If you clone by GitHub, skip this part) 
Place the downloaded **assets folder** into the root of the project directory. 
The game **will not run** unless the folder structure is correct.

```
Source/
│
├── assets/
│   ├── cat_happy.png
│   ├── cat_logo.png
│   ├── cat_sad.png
│   ├── words_of_5.txt 
│   ├── paw_print.png
│   ├── cat1.png
│   └── cat2.png
│
├── main.py
├── game.py
├── assets.py
├── settings.py
├── ...
├── requirements.txt
└── README.md
```

---

### Step 3: Install Dependencies

It’s recommended to use a **Python virtual environment**.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install the required libraries
pip install -r requirements.txt
```

---

### Step 4: Run the Game

Once assets and dependencies are in place:

```bash
python main.py
```

---

## Author Information

**Author:** Ngo Huynh Tham 

**Student ID:** 24127238
