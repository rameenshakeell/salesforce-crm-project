# AI-Powered Case Scoring on Salesforce Service Cloud

A working demo that combines a Salesforce Service Cloud support-case shell with a Python-based
risk-scoring pipeline, built to connect CRM configuration with data/AI-driven prioritization.

## The business problem

Support teams triage tickets manually: someone has to notice a ticket has been sitting too
long, or that a high-priority issue is quietly aging past its SLA. That's slow, inconsistent,
and doesn't scale as ticket volume grows. This project builds a small end-to-end system that:

1. Automatically routes incoming tickets to the right team.
2. Automatically escalates tickets that have been open too long.
3. Calculates a data-driven risk score per ticket, so the riskiest cases surface first,
   instead of relying on an agent noticing them.

## What's built

**Salesforce (Service Cloud):**
- Custom Case fields: `Days_Open__c`, `Risk_Score__c`, `Category__c` (Billing / Technical / General)
- Two Omni-Channel queues (Tier 1 Support, Billing Issues) with routing configured
- A Case Assignment Rule that auto-routes new cases to the correct queue based on Category
- A Record-Triggered Flow ("Case Auto-Escalation") that bumps a case's Priority to High once
  it's been open more than 3 days
- A Knowledge-style Article object with a sample support runbook

**Python:**
- `generate_fake_cases.py` generates 150 realistic synthetic support tickets (no real
  customer data was available for this demo project, so synthetic data was used to test the
  full pipeline end to end)
- `load_cases_to_salesforce.py` connects to Salesforce via the Bulk API and loads the
  synthetic tickets in as real Case records
- `score_cases.py` pulls case data back out of Salesforce via SOQL, calculates a risk score
  per case (a transparent weighted rule combining Priority and Days Open, not a trained ML
  model, since there's no historical outcome data to train on in a demo org), and writes the
  score back into the `Risk_Score__c` field

## What I'd track if this were live (adoption & ROI framing)

If this were deployed for a real support team, the metrics that would prove it's working:

- **% of high-risk cases (Risk Score > 0.7) resolved before SLA breach.** The core
  effectiveness metric; if this doesn't improve, the scoring isn't adding value.
- **Average time-to-escalation** for cases that eventually get flagged High priority. Should
  drop, since escalation is now automatic instead of manual.
- **Queue balance.** Whether Category-based routing is actually distributing load evenly, or
  whether one queue is consistently overloaded (a signal the routing rule itself needs
  rebalancing, not just more agents).
- **Adoption.** % of agents actually using the Risk Score field to prioritize their queue
  (visible via list view sort/filter usage) versus working tickets in raw creation order.

## Honest limitations of this demo

- Data is synthetic, not real customer data. There's no ground truth to validate the risk
  score against, so it's a transparent rule, not a trained/validated model.
- The Knowledge article uses a custom `Article` object instead of full Salesforce Knowledge,
  since Knowledge Article Type layout configuration was out of scope for a single demo article.
- Authentication uses a CLI-issued session token for local development. A production
  integration would use a proper OAuth Connected App / scheduled Named Credential instead.

## Setup

```
pip install -r requirements.txt
cp .env.example .env   # then fill in your real SF_SESSION_ID and SF_INSTANCE_URL
python generate_fake_cases.py
python load_cases_to_salesforce.py
python score_cases.py
```