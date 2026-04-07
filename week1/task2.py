ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ0123456789 "

def encrypt(plaintext, key):
    plaintext = plaintext.upper()
    ciphertext = ""

    for char in plaintext:
        index = ALPHABET.find(char)
        if index == -1:
            ciphertext += char
        else:
            new_index = (index + key) % len(ALPHABET)
            ciphertext += ALPHABET[new_index]

    return ciphertext

if __name__ == "__main__":
    plaintext = input("Input plaintext: ")
    key = int(input("Input an integer for encoding: "))

    result = encrypt(plaintext, key)
    print(result)

def decrypt(ciphertext, key):
    ciphertext = ciphertext.upper()
    plaintext = ""

    for char in ciphertext:
        index = ALPHABET.find(char)
        if index == -1:
            plaintext += char
        else:
            new_index = (index - key) % len(ALPHABET)
            plaintext += ALPHABET[new_index]

    return plaintext

if __name__ == "__main__":
    ciphertext = input("Input ciphertext: ")
    key = int(input("Input an integer for decoding: "))

    result = decrypt(ciphertext, key)
    print(result)