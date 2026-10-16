# Build with CoCo: SaaS Seat Sweeper

In this lab, you'll build SaaS Seat Sweeper, an internal Finance and IT application for finding unused software licenses. You'll start with a working read-only app, deploy it to Snowflake, add a feature that flags licenses for review, and deploy the updated version.

## What you'll do

- Explore the sample data and see how it becomes an app metric.
- Deploy the starter and open your own application URL.
- Try the access controls with a restricted test user.
- Use CoCo to add and test the license-review feature.
- Redeploy, check logs and costs, and clean up.

You'll also watch the facilitator ask a business-question agent about the same data and contracts. That agent is separate from CoCo and isn't something you need to build during this lab.

## How to work through the lab

Each person works individually. Open the repository root in CoCo and keep application changes in `starter-app/`.

Each exercise gives you a goal, a prompt to try, and a few things to check. Review what CoCo proposes before letting it make changes. Then try the result yourself. The workflow is **inspect, propose, approve, act, verify**.

Use the manual commands if you need them. If you get stuck, follow the recovery note or ask the facilitator; you don't need to solve every environment issue on your own.

## Before you start

For this version of the lab, the administrator prepares the account, sample data, governed views, and deployment prerequisites before the session. Your application is not deployed for you. You'll explore the data in Module 01 and perform both deployments yourself.

Keep your assigned account connection handy. Use only synthetic workshop data, and never paste passwords, tokens, or private keys into prompts or source files.

Flagging a license requests a review. It doesn't cancel a vendor subscription or prove that money has been saved.

## Three-hour agenda

The schedule includes a ten-minute break and ten minutes for cleanup. Aim to open your first deployed app by minute 65. Start with Module 00 below.
