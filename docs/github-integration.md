# GitHub Integration Guide

## 1. Webhook Setup
Configure a Webhook in your GitHub Organization or Repository:
- **Payload URL**: `https://YOUR_GREENOPS_HOST/api/v1/webhooks/github`
- **Content type**: `application/json`
- **Secret**: Value of `GITHUB_WEBHOOK_SECRET`
- **Events**: `Pull requests`, `Workflow runs`

## 2. In-Place Scorecard Updating
GreenOps maintains an idempotent PR comment containing the anchor `<!-- greenops-scorecard -->`. When subsequent commits are pushed or workflow telemetry finishes, the existing comment is updated cleanly rather than spamming the PR.

## 3. Workflow Dispatch for Deferred Runs
Eligible workflows (e.g. `.github/workflows/greenops-demo.yml`) are triggered automatically when the scheduler determines an optimal lower-carbon execution window.
