# Put your first project on GitHub

Recommended repository name: **atc-guardian**

Repository description:

> Pilot-inspired ATC research simulator with clearance memory, traffic and weather monitoring, and human takeover. Python + React. Simulation only.

Suggested topics: `aviation`, `simulation`, `air-traffic-control`, `python`, `fastapi`, `react`, `typescript`, `safety-engineering`.

## Upload the source, not just the ZIP

The ZIP is your download package. GitHub should show **README.md, backend, frontend, docs, tests, scenarios**, and the other project files directly at the repository root. Uploading only a ZIP makes the code hard to review.

## First upload with Git

1. Install [Git](https://git-scm.com/downloads) if needed.
2. On [GitHub](https://github.com/new), create an empty repository named `atc-guardian`. Choose the visibility you want. Leave the README, license, and gitignore initialization options unchecked; these files are included here.
3. Open a terminal in the extracted `atc-guardian` folder and run:

```bash
git init -b main
git add .
git status
git commit -m "Add ATC Guardian v0.1 research simulator"
```

4. Copy the repository's HTTPS URL from GitHub. Replace `YOUR-USERNAME` below with your account name:

```bash
git remote add origin https://github.com/YOUR-USERNAME/atc-guardian.git
git push -u origin main
```

Git may open a browser for sign-in. If it asks for commit identity, set your desired public name and your GitHub-provided private/noreply commit email. You can find that email in GitHub's email settings.

The included `.gitignore` excludes dependencies, local databases, generated builds, and `.env` files. Review `git status` before committing. Keep the `package-lock.json` and `requirements.txt` files; they record the tested dependencies.

## Using the website instead

Create the repository, choose **Add file → Upload files**, and upload the extracted source files/folders. Ensure README.md is at the top level. Include `.github/workflows/ci.yml` and `.gitignore` if your file picker shows them. Use the Git method for ongoing updates and consistent handling of those configuration files.

Do not upload `.venv`, `frontend/node_modules`, `frontend/dist`, `data`, or test-output folders created by setup. The original downloaded package does not contain those folders.

## After the upload

Check that the README screenshot appears and browse the source. Open **Actions** to see the included checks run. Pin the repository on your profile if you want it featured. You can later create a `v0.1.0` release and attach the download package.

The project was not uploaded to your GitHub account during this handoff. The included CI configuration has not run on your account yet.

## What the repository demonstrates

It gives you concrete code to discuss: aircraft state, geometry, input validation, testing, a real-time interface, event recording, and careful limits. Reproduce the demo and read the learning guide before presenting the technical details as things you understand.

## Official instructions

- [GitHub: add locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub: upload files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

Checked 2026-10-05. GitHub's labels can change; the source belongs at the repository root.
