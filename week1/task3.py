VOWELS = set("AEIOUÅÄÖaeiouåäö")

def main():
    text = input("Input a text to be analyzed: ")

    # total characters
    char_count = len(text)

    # split into words (space-delimited)
    words = text.split()
    word_count = len(words)

    # word frequencies (case insensitive, keep insertion order)
    frequencies = {}
    for word in words:
        key = word.lower()
        if key not in frequencies:
            frequencies[key] = 0
        frequencies[key] += 1

    # text with each word reversed
    reversed_words = []
    for word in words:
        reversed_words.append(word[::-1])
    reversed_text = " ".join(reversed_words)

    # text with only words starting with a vowel (from reversed_words)
    vowel_words = []
    for word in reversed_words:
        if word and word[0] in VOWELS:
            vowel_words.append(word)
    vowel_text = " ".join(vowel_words)

    # output
    print("Characters:", char_count)
    print("Words:", word_count)
    print("Word frequencies:")
    for word, count in frequencies.items():
        print(f"{word}: {count}")
    print("Text with reversed words:", reversed_text)
    print("Text with words not starting with a vowel removed:", vowel_text)

if __name__ == "__main__":
    main()
