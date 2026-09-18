"""
Reads churn-scored customer data and loads it into this org as Lead records, so the churn risk
score and risk band are visible directly in the CRM.

Uses the same .env file as load_cases_to_salesforce.py.
"""

import csv
import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

SESSION_ID = os.environ["SF_SESSION_ID"]
INSTANCE_URL = os.environ["SF_INSTANCE_URL"]

sf = Salesforce(instance_url=INSTANCE_URL, session_id=SESSION_ID)
print("Connected to Salesforce successfully.")

records = []
with open("data/churn_scored.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "LastName": f"Customer {row['customer_id']}",
            "Company": f"{row['industry']} Account {row['customer_id']}",
            "Churn_Risk_Score__c": round(float(row["predicted_churn_probability"]), 2),
            "Risk_Band__c": row["churn_risk_band"],
        })

print(f"Loaded {len(records)} scored leads from the CSV, inserting into Salesforce now...")

results = sf.bulk.Lead.insert(records)

successes = sum(1 for r in results if r["success"])
failures = [r for r in results if not r["success"]]

print(f"Done. {successes} leads created successfully.")
if failures:
    print(f"{len(failures)} records failed. First failure details:")
    print(failures[0])