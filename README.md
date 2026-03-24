# PERIODIZE — Setup Guide

## What you're building
A private GitHub repo that:
- Hosts a web app at `https://YOUR-USERNAME.github.io/periodize`
- Automatically parses your shorthand workout logs into JSON
- Shows dashboards, progress charts, and PRs on your phone

Total setup time: ~15 minutes, one-time only.

---

## Step 1 — Create the GitHub repository

1. Go to [github.com](https://github.com) and sign in (or create an account)
2. Click **+** → **New repository**
3. Name it `periodize`
4. Set it to **Public** *(required for free GitHub Pages)*
5. Click **Create repository**

---

## Step 2 — Upload the files

You need to create this folder structure in your repo:

```
periodize/
├── index.html
├── scripts/
│   └── parse_workout.py
├── .github/
│   └── workflows/
│       └── parse.yml
├── logs/
│   ├── raw/        ← your shorthand .txt files go here
│   └── json/       ← auto-generated JSON goes here
```

### Upload via GitHub website:

1. In your repo, click **Add file** → **Create new file**
2. For each file below, paste the name in the path box and the content in the editor

**File 1:** Name = `index.html` → paste contents of index.html

**File 2:** Name = `scripts/parse_workout.py` → paste contents of parse_workout.py

**File 3:** Name = `.github/workflows/parse.yml` → paste contents of parse.yml

**File 4:** Name = `logs/raw/.gitkeep` → leave content empty (creates the folder)

**File 5:** Name = `logs/json/.gitkeep` → leave content empty (creates the folder)

Commit each file with the green **Commit new file** button.

---

## Step 3 — Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages** (left sidebar)
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main`, Folder: `/ (root)`
4. Click **Save**

Your app will be live at:
`https://YOUR-USERNAME.github.io/periodize`

*(Takes 1-2 minutes the first time)*

---

## Step 4 — Create a Personal Access Token

This lets the web app commit your workout logs directly from your phone.

1. Go to [github.com/settings/tokens/new](https://github.com/settings/tokens/new)
2. Note: `periodize app`
3. Expiration: `No expiration` (or 1 year for security)
4. Scopes: tick **repo** (top-level checkbox)
5. Click **Generate token**
6. **Copy the token** — you only see it once. Save it somewhere safe (password manager).

---

## Step 5 — Configure the web app

1. Open `https://YOUR-USERNAME.github.io/periodize` on your phone
2. Enter:
   - **GitHub Username**: your username
   - **Repository Name**: `periodize`
   - **Personal Access Token**: the token from Step 4
3. Tap **Save & Enter**

This is stored in your browser only — never sent anywhere except GitHub.

---

## Step 6 — Log your first workout

Open the app, tap **+ Log**, and enter your workout in shorthand:

```
2026-03-24 | 1 | accumulation | 7 | Felt good
Squat: 100x5@8, 100x5@8.5, 102.5x5@9
Bench: 80x5@7, 82.5x5@8
RDL: 70x8@7, 70x8@7.5
```

Tap **Commit to GitHub**. The GitHub Action will:
1. Detect the new `.txt` file in `logs/raw/`
2. Parse it into JSON in `logs/json/`
3. The dashboard will reload automatically after ~35 seconds

---

## Shorthand Format Reference

```
DATE | WEEK | PHASE | SESSION_RPE | NOTES
ExerciseName: WEIGHTxREPS@RPE, WEIGHTxREPS@RPE
```

- **DATE**: `YYYY-MM-DD` format
- **WEEK**: integer (1, 2, 3...)
- **PHASE**: `accumulation`, `intensification`, `deload`, or anything you like
- **SESSION_RPE**: 1–10, how hard the overall session felt
- **NOTES**: optional free text
- **@RPE**: optional per set, omit if not using

### Phase naming suggestions for periodization:
- `accumulation` — high volume, moderate intensity
- `intensification` — lower volume, high intensity
- `deload` — low volume, low intensity
- `peak` — competition prep

---

## Troubleshooting

**App shows "Could not load workouts"**
→ Check your token has `repo` scope and hasn't expired
→ Make sure the repo name matches exactly

**GitHub Action not running**
→ Go to repo → Actions tab → check if workflows are enabled
→ Look at the failed run for error details

**Parse error on my workout**
→ Check format: `Weight` must be a number, `x` then reps, `@` then RPE
→ Each exercise must have a colon after the name
→ Header must have pipes `|` separating all fields

---

## Keeping the token secure

Your token gives write access to your repo. It's stored in `localStorage` in your phone browser — this is fine for personal use. If you ever think it's compromised, go to GitHub Settings → Tokens and regenerate it, then update the app config.
