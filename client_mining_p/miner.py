import hashlib
import requests
import datetime
import math

import sys

def check_if_new_proof_on_chain(last_proof):
    r = requests.get(url=node + "/last_proof")
    data = r.json()
    return data.get('proof') != last_proof

def proof_of_work(last_proof):
    """
    Simple Proof of Work Algorithm
    - Find a number p' such that hash(pp') contains 6 leading
    zeroes, where p is the previous p'
    - p is the previous proof, and p' is the new proof
    """
    print("Searching for next proof")
    proof = 0
    startTime = datetime.datetime.now()
    proof_counter = 1
    while valid_proof(last_proof, proof) is False:
        proof += 1
        if proof > proof_counter*10000000:
            proof_counter += 1
            didGetSolved = check_if_new_proof_on_chain(last_proof)
            currentTime = datetime.datetime.now()
            delta = math.floor(currentTime.timestamp() - startTime.timestamp())
            print("Elapsed: " + str(delta))
            print("proof: " + str(proof))
            if didGetSolved == True:
                print("Too slow: someone else solved")
                return proof
    endTime = datetime.datetime.now()
    finalTime = math.floor(endTime.timestamp() - startTime.timestamp())
    print("Proof found: " + str(proof))
    print("Time taken: " + str(finalTime))
    return proof

def valid_proof(last_proof, proof):
    """
    Validates the Proof:  Does hash(last_proof, proof) contain 6
    leading zeroes?
    """
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:6] == "000000"

if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0
    # Run forever until interrupted
    while True:
        # Get the last proof from the server
        r = requests.get(url=node + "/last_proof")
        data = r.json()
        new_proof = proof_of_work(data.get('proof'))

        post_data = {"proof": new_proof}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()
        if data.get('message') == 'New Block Forged':
            coins_mined += 1
            print("Total coins mined: " + str(coins_mined))
        else:
            print(data.get('message'))
