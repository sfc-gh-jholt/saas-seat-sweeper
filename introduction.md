# Build with CoCo: SaaS Seat Sweeper

In this lab, you'll build SaaS Seat Sweeper, an internal Finance and IT application that identifies inactive SaaS licenses, shows contract context, and flags assignments for reclamation review. You'll start with a prepared read-only application and use Cortex Code to deploy it, add a meaningful feature, and verify the change in a second deployment.

## What you will do

- **Understand and prepare the data contract.** Inspect how the synthetic dataset is built, identify the assignment grain and join keys, and trace a displayed metric through the governed views. Check the prepared data rather than treating it as a black box.
- **Ship the first version.** Review deployment settings, approve the target, and open your own authenticated application endpoint.
- **Challenge the access model.** Check what app-entry permissions and SQL policies actually prove about who can see or change data.
- **Build and verify a feature.** Ask CoCo for a plan, review the changes, test reclamation, and deploy the updated application.
- **Operate and evaluate.** Inspect logs and cost boundaries, watch a separate business-question agent demo, compare responsibilities with your current stack, and clean up.

## How you will work with CoCo

You will practice **inspect, propose, approve, act, verify** throughout the lab. The prompt cards provide bounded starting points, not answers to accept uncritically. Review proposed actions, inspect source and tool evidence, and use focused follow-ups when something is missing or wrong.

Each person works individually in their own prepared account and application project. You direct CoCo, review its proposals, and verify the results yourself. Take the full scheduled break before feature work. Manual commands and recovery checkpoints are available when needed; record when you use them.

CoCo is your development and operations assistant. The facilitator's Cortex Agent is a separate demonstration of answering business questions at runtime; building that agent is not part of the participant path.

## What is prepared, and what is yours

The administrator prepares the eligible account, synthetic data, governed views, and approved prerequisites before the timer. In Module 01, you inspect that build recipe and validate a baseline before your first deployment. The [dataset build guide](dataset-guide.md) explains the source tables, seed process and adaptation to your own data. You receive the application source, but your participant deployment and endpoint do not exist yet. You perform both deployments and the feature work.

This lab is designed for application developers and data engineers. Both follow the same path. You do not need to scaffold an entire app or manually build its container infrastructure.

By the end, your evidence should include your first endpoint, a reviewed feature surviving redeployment, tested access boundaries, and a cleanup or explicit retention record. Flagging a license requests review: it does not cancel a vendor seat or prove realized savings.

## Three-hour agenda

The schedule below includes the ten-minute break and ten-minute cleanup. Times are elapsed from the session start. The first endpoint target is minute 65; account preparation happens before the session. This introduction is a navigation page, not an additional timed exercise.
