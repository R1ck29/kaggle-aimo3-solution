#!/usr/bin/env bash
set -euo pipefail

# Push current repo to GitHub using HTTPS + PAT.
# Required env:
#   GITHUB_PAT  - fine-grained or classic token with repo write access
#   GITHUB_REPO - e.g. R1ck29/kaggle-aimo3-solution

if [[ -z "${GITHUB_PAT:-}" ]]; then
  echo "GITHUB_PAT is required."
  exit 1
fi

if [[ -z "${GITHUB_REPO:-}" ]]; then
  echo "GITHUB_REPO is required (e.g. R1ck29/kaggle-aimo3-solution)."
  exit 1
fi

git branch -M main

git remote remove origin >/dev/null 2>&1 || true
git remote add origin "https://R1ck29:${GITHUB_PAT}@github.com/${GITHUB_REPO}.git"

git push -u origin main
