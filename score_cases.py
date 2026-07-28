"""
Pulls case data OUT of Salesforce, calculates a risk score for each case,
then writes those scores BACK into the Risk Score field on each record.

Reads connection details from local .env file (see load_cases_to_salesforce.py
for setup instructions -- same .env is reused here). If your token has expired,
rerun: sf org auth show-access-token -o myproject
and update SF_SESSION_ID in your .env file with the new value.
"""

import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

SESSION_ID = os.environ["SF_SESSION_ID"]
INSTANCE_URL = os.environ["SF_INSTANCE_URL"]

sf = Salesforce(instance_url=INSTANCE_URL, session_id=SESSION_ID)
print("Connected to Salesforce successfully.")

# ---- Step 1: Pull case data OUT of Salesforce ----
# SOQL is Salesforce's version of SQL -- this asks for the fields we need
# from every case that isn't Closed.
query = """
    SELECT Id, Priority, Days_Open__c
    FROM Case
    WHERE Status != 'Closed'
"""
result = sf.query_all(query)
cases = result["records"]
print(f"Pulled {len(cases)} cases from Salesforce.")

# ---- Step 2: Calculate a risk score for each case ----
# This is a simple, transparent scoring rule (not a trained ML model) --
# it combines how long a case has been open with its priority level.
# Priority is weighted more heavily since a High-priority case that's
# also been open a while is the riskiest combination.
priority_weight = {"Low": 0.2, "Medium": 0.5, "High": 0.9, None: 0.3}

scored_updates = []
for case in cases:
    days_open = case.get("Days_Open__c") or 0
    priority = case.get("Priority")

    # Normalize days_open to a 0-1 scale, capping at 10 days
    days_component = min(days_open / 10, 1.0)
    priority_component = priority_weight.get(priority, 0.3)

    # Weighted blend: priority matters slightly more than raw days open
    risk_score = round((priority_component * 0.6) + (days_component * 0.4), 2)

    scored_updates.append({
        "Id": case["Id"],
        "Risk_Score__c": risk_score,
    })

print("Calculated risk scores for all cases. Example of first 5:")
for row in scored_updates[:5]:
    print(row)

# ---- Step 3: Write the scores BACK into Salesforce ----
results = sf.bulk.Case.update(scored_updates)

successes = sum(1 for r in results if r["success"])
failures = [r for r in results if not r["success"]]

print(f"Done. {successes} cases updated with a Risk Score.")
if failures:
    print(f"{len(failures)} updates failed. First failure details:")
    print(failures[0])