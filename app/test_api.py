import requests
import json
import os

# API endpoint
url = "http://localhost:8000/process-documents"

# Get the directory of the current script
base_dir = "/Users/hawhee/projects/anchorai/project-boilerplate"

# Sample files
files = [
    ('files', ('BL-COSU534343282.pdf', open(os.path.join(base_dir, 'BL-COSU534343282.pdf'), 'rb'), 'application/pdf')),
    ('files', ('Demo-Invoice-PackingList_1 (1).xlsx', open(os.path.join(base_dir, 'Demo-Invoice-PackingList_1 (1).xlsx'), 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
]

try:
    # Send POST request
    response = requests.post(url, files=files)
    
    # Close files
    for _, file_info in files:
        file_info[1].close()
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("API Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error calling API: {e}")