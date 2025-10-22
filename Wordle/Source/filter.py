# filter_words.py

# Input and output file paths
input_file = "wordlist.txt"
output_file = "words_of_5.txt"

# Open and process the file
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        word = line.strip()  # remove spaces/newlines
        if len(word) == 5 and word.isalpha():
            outfile.write(word.lower() + "\n")  # save lowercase version
