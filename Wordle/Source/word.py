import random 
import sys

def check_guess(guess, secret): 
    guess_str = "".join(guess)
    feedback = []
    secret_list = list(secret)

    for i in range(len(guess_str)): 
        if guess_str[i] == secret_list[i]:
            feedback.append("green")
            secret_list[i] = None
        else: 
            feedback.append(None)
    
    for i in range(len(guess_str)): 
        if feedback[i] == None:
            if guess_str[i] in secret_list:
                feedback[i] = "yellow"
                secret_list.remove(guess_str[i])
            else:
                feedback[i] = "gray"
    return feedback

def load_words():
    try:
        with open("words_of_5.txt", "r") as f:
            words = [line.strip().upper() for line in f.readlines()]
        return words
    except FileNotFoundError:
        print("Error: wordlist.txt not found!")
        sys.exit()
