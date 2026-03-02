# Git Push Workflow (Kaggle AIMO3)

Purpose
- Record the exact push flow used in this repo.
- Provide a safe, repeatable automation path (HTTPS + PAT).

Summary of the flow used
- Initialize git and commit locally.
- Set remote to GitHub.
- Use HTTPS + PAT for authentication (SSH failed due to host key mismatch).
- Push `main` to `origin`.

One-time setup (local)
1) Initialize and commit
```bash
git init
git add .
git commit -m "Initialize AIMO3 notebook workflow"
```

2) Add remote
```bash
git remote add origin https://github.com/R1ck29/kaggle-aimo3-solution.git
```

3) Rename branch to main
```bash
git branch -m main
```

4) Push (HTTPS + PAT)
```bash
git push -u origin main
```
When prompted:
- Username: `R1ck29`
- Password: your PAT

Security notes
- Never paste a PAT into a command line or store it in plain text files.
- If a PAT was ever pasted into chat/terminal output, revoke it immediately and create a new one.

Why HTTPS + PAT (not SSH)
- SSH push failed with "REMOTE HOST IDENTIFICATION HAS CHANGED".
- To avoid editing `~/.ssh/known_hosts`, we used HTTPS + PAT.

Automation (safe)
- Use `scripts/push_github.sh` with an environment variable:
```bash
export GITHUB_PAT="YOUR_PAT"
export GITHUB_REPO="R1ck29/kaggle-aimo3-solution"
./scripts/push_github.sh
```
- The script avoids printing the PAT and does not store it on disk.

