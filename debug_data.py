import json
import os

file_path = 'data.json'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    with open(file_path, 'r') as f:
        data = json.load(f)

    target_pk = "f9d7ca59-c25b-4f77-8678-e0f6b659fd42"
    
    found = False
    for item in data:
        if item.get('model') == 'students.student' and item.get('pk') == target_pk:
            print(f"Found record: {item}")
            fields = item.get('fields', {})
            for k, v in fields.items():
                if isinstance(v, str) and len(v) > 20:
                    print(f"Field '{k}' has length {len(v)}: '{v}'")
            found = True
            break
    
    if not found:
        print("Record not found via exact PK match.")
        
except Exception as e:
    print(f"Error: {e}")
