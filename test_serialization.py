import sys
import os
import json
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from backend.rag_retriever import get_retriever

def check_for_numpy(obj, path="root"):
    if isinstance(obj, (np.integer, np.floating, np.ndarray)):
        print(f"FOUND NUMPY TYPE at {path}: {type(obj)} - {obj}")
        return True
    
    found = False
    if isinstance(obj, dict):
        for k, v in obj.items():
            if check_for_numpy(v, path=f"{path}.{k}"):
                found = True
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if check_for_numpy(v, path=f"{path}[{i}]"):
                found = True
    return found

print("Initializing Retriever...")
retriever = get_retriever()
print("Searching...")
items = retriever.retrieve_items("Vegetarian Chowfun")

print("\nChecking results for numpy types...")
if check_for_numpy(items):
    print("FAIL: Numpy types found in output.")
else:
    print("SUCCESS: Output is clean.")

print("\nAttempting JSON serialization...")
try:
    json.dumps(items)
    print("SUCCESS: JSON serialization worked.")
except Exception as e:
    print(f"FAIL: JSON serialization failed: {e}")
