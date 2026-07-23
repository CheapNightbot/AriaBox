# Contributing to AriaBox ⨾💿˚.⋆

Thank you for your interest in contributing to AriaBox! Whether you are fixing a bug, adding a new feature, or just improving the documentation, your help is deeply appreciated.

Before you start, please read this guide to make sure your contribution fits smoothly into the project.

## 🌸 Ethical Guidelines

AriaBox is built with a strong focus on ethical use.
- **Support Artists:** We strongly encourage users to support artists and purchase music whenever possible.
- **Safe Alternative:** Optional features exist strictly as a safe, clean alternative to sketchy third-party sites for hard-to-find audio (like personal cover song instrumentals).
- **Respect Copyright:** Please do not contribute code that bypasses DRM, promotes piracy, or violates the terms of service of the music APIs we use.

## 🛠️ Development Setup

For the best experience, we recommend using the included `.devcontainer`, which has all dependencies pre-installed.

If you prefer to develop on your host machine, you must first install the core tech stack:
- **Python 3.x** & **uv** (for backend dependency management)
- **Node.js** & **pnpm** (for frontend development)
- **ffmpeg** (required for audio processing and format conversion)

Once installed, follow the "Development" section in the [README.md](./README.md#development) to spin up the backend and frontend servers.

## 💬 Commit Messages & Release Notes

To keep our project history clean and to automatically generate beautiful release notes, we use **Conventional Commits**.

When you commit your changes, please start your commit message with one of the following prefixes:

| Prefix | Description | Example |
| :--- | :--- | :--- |
| `feat:` | A new feature or enhancement. | `feat: add organized library auto-save` |
| `fix:` | A bug fix or error resolution. | `fix: resolve SimpleNamespace type error` |
| `docs:` | Changes to documentation or README. | `docs: update README with Podman instructions` |
| `chore:` | Maintenance, dependencies, or CI/CD. | `chore: update GitHub Actions workflow` |
| `style:` | Code formatting (no logic change). | `style: fix indentation in download.py` |

**Note:** If you forget a prefix, don't worry! Your commit will still be included in the release notes under the "General Updates" section, but using the correct prefix helps keep the changelog beautifully organized.

## 🚀 How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** and ensure they work locally.
3. **Commit your changes** using the prefixes mentioned above.
4. **Push to your fork** and open a **Pull Request (PR)** against the `main` branch of this repository.
5. **Describe your PR:** Please explain what you changed and why. If it fixes a bug, let us know how to reproduce it.

## 🎀 Code of Conduct

- Be kind, respectful, and constructive in all discussions.
- If you are unsure about something, just ask! We are all here to learn and build together.

Thank you for helping make AriaBox better! ( ˶ˆ ᵕ ˆ˶ )
