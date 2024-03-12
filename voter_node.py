import requests
import json
from crypto_otrs import ring

# Configuration
CENTRAL_AUTHORITY_URL = "http://127.0.0.1:5000"
BLOCKCHAIN_SERVER_URL = "http://127.0.0.1:5001"

PRIVATE_KEY = None
PUBLIC_KEY = None

def generate_rsa_key():
    public_key, private_key = ring.keygen()
    
    return private_key, public_key

def register_public_key(public_key):
    response = requests.post(f"{CENTRAL_AUTHORITY_URL}/register", json={"public_key": public_key})
    print(response.json().get('message'))

def get_registered_public_keys():
    response = requests.get(f"{CENTRAL_AUTHORITY_URL}/public_keys")
    public_keys = response.json()["public_keys"]
    print(f"Number of registered public keys: {len(public_keys)}")
    return [key for key in public_keys]

def fetch_blockchain():
    response = requests.get(f"{BLOCKCHAIN_SERVER_URL}/chain")
    blockchain = response.json()
    print_blockchain(blockchain)
    return blockchain

def print_blockchain(blockchain):
    print("Current Blockchain State:")
    for block in blockchain:
        print(json.dumps(block, indent=4, sort_keys=True))

def cast_vote(vote_message):
    print(PRIVATE_KEY)
    if PRIVATE_KEY is None or PUBLIC_KEY is None :
        print("First create and register keys")
        return

    ring_ = [public_key for public_key in get_registered_public_keys()]
    print(ring_)
    print(PUBLIC_KEY)
    position = ring_.index(PUBLIC_KEY)
    signature = ring.RSign(ring_, PRIVATE_KEY, position, vote_message.encode())
    
    # Prepare and submit the vote block with the signature
    vote_block = {
        'message': vote_message,
        'signature': signature
    }

    submit_vote(vote_block)

def submit_vote(block):
    response = requests.post(f"{BLOCKCHAIN_SERVER_URL}/vote", json=block)
    print(response.json().get('message'))

def main_menu():
    print("\nVoter Node Operations:")
    print("1. Generate and Register Public Key")
    print("2. Cast a Vote")
    print("3. Print Blockchain")
    print("4. Print Number of Registered Public Keys")
    print("5. Exit")
    return input("Choose an action: ")

def main():
    while True:
        choice = main_menu()
        if choice == "1":
            global PRIVATE_KEY
            global PUBLIC_KEY
            PRIVATE_KEY, PUBLIC_KEY = generate_rsa_key()
            print("Your Private Key (keep it safe):", PRIVATE_KEY)
            register_public_key(PUBLIC_KEY)
        elif choice == "2":
            vote_message = input("Enter your vote: ")
            cast_vote(vote_message)
        elif choice == "3":
            fetch_blockchain()
        elif choice == "4":
            get_registered_public_keys()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
