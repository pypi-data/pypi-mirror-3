import random

characters = "abcdefghijklmnopqrstuvwxyz"
characters += characters.upper()
characters += "0123456789"

def generate_nonce(count=20):
    """Generates a random nonce."""
    nonce = ""
    for step in range(count):
        nonce += random.choice(characters)
    return nonce

if __name__ == '__main__':
    print 'nonce:', generate_nonce()