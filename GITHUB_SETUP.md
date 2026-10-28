# Putting this project on GitHub

These steps create a **private** GitHub repository called `thanvi-khutbat` under your personal account **iatasadduq** and upload this folder to it. Do this once, before starting the new chat.

Run each command in **Terminal**, one at a time, on the Mac account you will use for this project. Text after `#` is an explanation; don't type it.

---

## Step 1: Check which GitHub account you are signed in to

```bash
gh auth status
```

It should say **Logged in to github.com account iatasadduq**.

- If it shows a different account, or says you are not logged in, run the command below. Choose **GitHub.com** and **HTTPS**, sign in through the browser with the `iatasadduq` account, then run `gh auth status` again.

```bash
gh auth login
```

- If Terminal says `gh: command not found`, install the GitHub tool first with the command below, then repeat Step 1. (This needs Homebrew, which is already on this Mac.)

```bash
brew install gh
```

## Step 2: Go to the project folder

```bash
cd /Users/Shared/Mewaiz
```

## Step 3: One-time Git settings for this Mac account

Allow Git to work in a folder that is shared between Mac accounts:

```bash
git config --global --add safe.directory /Users/Shared/Mewaiz
```

Set the name and email that appear on your saved versions (commits):

```bash
git config --global user.name "Imran Tasadduq"
```

```bash
git config --global user.email "iatasadd@alumni.uwo.ca"
```

## Step 4: Tell Git which files to ignore

Mac system files (`.DS_Store`) should not be uploaded:

```bash
printf '.DS_Store\n' > .gitignore
```

## Step 5: Create the repository on your Mac and save a first version

```bash
git init -b main
```

```bash
git add .
```

```bash
git commit -m "Initial upload: 32 scanned volumes, Volume 1 pilot, tools, handoff"
```

The `git add .` step may take a minute because the 32 PDFs total about 760 MB.

## Step 6: Create the private repository on GitHub and upload

```bash
gh repo create thanvi-khutbat --private --source=. --push
```

The upload is about 760 MB, so it can take 10–30 minutes depending on your internet speed. Leave Terminal open until it finishes.

If the upload stops with an error such as `RPC failed` or `HTTP 400`, run this once and then try the push again:

```bash
git config --global http.postBuffer 524288000
```

```bash
git push -u origin main
```

## Step 7: Check that it worked

Open **https://github.com/iatasadduq/thanvi-khutbat** in your browser. Check that:

- it shows a **Private** label next to the name
- you can see `HANDOFF.md`, `GITHUB_SETUP.md`, `scanned_version`, `tools` and `Index pilot - 01 dunya o akhiret`
- `scanned_version` contains 32 PDFs

---

## Starting the new chat in the cloud

1. Go to **claude.ai/code**, signed in with your **personal** Claude account.
2. If asked, connect GitHub and allow access to the `thanvi-khutbat` repository.
3. Start a new session on the **thanvi-khutbat** repository.
4. Make your first message: **"Read HANDOFF.md and continue from where it leaves off."**

## Later: getting the cloud session's work back to your Mac

The cloud session saves its work to GitHub. To bring those changes into this folder, run:

```bash
cd /Users/Shared/Mewaiz
```

```bash
git pull
```

## If you change files on your Mac and want them on GitHub

```bash
cd /Users/Shared/Mewaiz
```

```bash
git add . && git commit -m "Describe what changed" && git push
```
