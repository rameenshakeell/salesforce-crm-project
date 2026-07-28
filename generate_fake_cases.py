"""
Generates fake but realistic support-case data 
"""

import csv
import random

# ---- Pools of realistic values to randomly pick from ----

subjects_by_category = {
    "Billing": [
        "Payment declined at checkout",
        "Duplicate charge on my card",
        "Question about invoice amount",
        "Refund not received yet",
        "Unexpected charge on my account",
        "Billing address needs updating",
    ],
    "Technical": [
        "App crashes on login",
        "Can't reset my password",
        "Page won't load",
        "Error message when saving changes",
        "Mobile app freezing on startup",
        "Feature not working as expected",
    ],
    "General": [
        "Question about account settings",
        "How do I update my email address",
        "Where can I find my order history",
        "General feedback about the product",
        "Question about subscription plans",
        "Need help navigating the dashboard",
    ],
}

categories = ["Billing", "Technical", "General"]
priorities = ["Low", "Medium", "High"]

NUM_ROWS = 150  

rows = []
for i in range(NUM_ROWS):
    category = random.choice(categories)
    subject = random.choice(subjects_by_category[category])

    # Make priority and days_open loosely related (older tickets skew higher priority),
    # so the data isn't purely random noise -- it behaves a bit like a real support queue.
    days_open = random.randint(0, 10)
    if days_open >= 6:
        priority = random.choices(priorities, weights=[1, 2, 5])[0]
    elif days_open >= 3:
        priority = random.choices(priorities, weights=[2, 5, 2])[0]
    else:
        priority = random.choices(priorities, weights=[5, 3, 1])[0]

    rows.append({
        "Subject": subject,
        "Category__c": category,   
        "Priority": priority,
        "Days_Open__c": days_open,
        "Status": "New" if days_open <= 1 else "Working",
        "Origin": random.choice(["Phone", "Web", "Email"]),
    })

# ---- Write to CSV ----
fieldnames = ["Subject", "Category__c", "Priority", "Days_Open__c", "Status", "Origin"]

with open("fake_cases.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done! Created fake_cases.csv with {NUM_ROWS} fake support cases.")
