"""
Connects to your Salesforce org using the CLI-generated session token and
loads the fake_cases.csv data in as real Case records.

Setup (one-time):
1. Copy .env.example, rename the copy to ".env".
2. In your terminal, run: sf org display -o myproject --verbose --json
   -> copy the "instanceUrl" value into .env as SF_INSTANCE_URL.
3. In your terminal, run: sf org auth show-access-token -o myproject
   -> copy the token it prints into .env as SF_SESSION_ID.

"""

import csv
import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv() 

SESSION_ID = os.environ["SF_SESSION_ID"]
INSTANCE_URL = os.environ["SF_INSTANCE_URL"]

# Connect to Salesforce using the existing CLI session (bypasses username/password/OAuth entirely)
sf = Salesforce(instance_url=INSTANCE_URL, session_id=SESSION_ID)
print("Connected to Salesforce successfully.")

# Read the CSV file 
records = []
with open("fake_cases.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "Subject": row["Subject"],
            "Category__c": row["Category__c"],
            "Priority": row["Priority"],
            "Days_Open__c": int(row["Days_Open__c"]),
            "Status": row["Status"],
            "Origin": row["Origin"],
        })

print(f"Loaded {len(records)} fake cases from the CSV, inserting into Salesforce now...")

# Insert all records at once using the Bulk API (much faster than one at a time)
results = sf.bulk.Case.insert(records)

# Count successes and failures
successes = sum(1 for r in results if r["success"])
failures = [r for r in results if not r["success"]]

print(f"Done. {successes} cases created successfully.")
if failures:
    print(f"{len(failures)} records failed. First failure details:")
    print(failures[0])