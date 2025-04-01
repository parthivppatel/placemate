import random
import string

def generate_random_password():
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Randomly select characters and combine them into a password
    password = ''.join(random.choice(characters) for _ in range(12))
    
    return password