# AriaBox ⨾💿✮˚.⋆

A full-stack web application to add and update music metadata, convert between audio formats, and optionally download music with metadata baked in.

> [!NOTE]
> The downloading feature is disabled by default. If possible, please support artists and purchase the music you love! This feature exists solely to provide a safe, clean alternative to sketchy download sites for hard-to-find audio.

## Key Features

- **Metadata Tagging:** Search across multiple music services and manually apply metadata to your local audio files.
- **Organized Library:** Optionally auto-save processed files into a clean, browsable folder structure (`Artist / Album (Year) / Track.ext`) to keep your collection tidy.
- **Audio Conversion:** A dedicated, separate feature to convert your audio files between different audio formats.
- **Multi-Service Search:** Fetch rich metadata seamlessly from Deezer, YouTube Music, and iTunes/Apple Music.

## Tech Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Python, Flask, Waitress, `uv`
- **Audio & API Engine:** `ffmpeg` (for audio processing), `yutipy` (for music service APIs)
- **Infrastructure:** Docker, Podman, Docker Compose

## Project Structure

This project is structured as a monorepo, keeping the backend and frontend codebases separate but working together seamlessly.

```text
.
├── .devcontainer/    # VS Code Dev Container configuration for seamless development
├── backend/          # Backend logic, API routes, and configuration
├── data/             # Persistent storage for settings, secrets, and library (created at runtime)
├── frontend/         # Frontend UI, components, and Vite configuration
├── .env.example      # Example environment variables for the whole application
├── compose.yml       # Docker Compose configuration
├── Dockerfile        # Multi-stage build for production
├── README.md         # You are here!
└── run.sh            # Interactive launcher script
```

## Configuration & Environment Variables

AriaBox uses environment variables to configure the entire application. You can define these in two ways:
1. By creating a `.env` file in the project root (copy `.env.example` to get started).
2. By passing them directly in the `environment` section of `compose.yml`.

| Variable           | Default (Local)  | Default (Docker) | Description                                                                                            |
| :----------------- | :--------------- | :--------------- | :----------------------------------------------------------------------------------------------------- |
| `DATA_DIR`         | `./data`         | `/app/data`      | Directory for settings, secrets, and your organized music library. *Local runs:* Relative to project root.  *Container runs:* Path inside the container. |
| `DEFAULT_LANGUAGE` | `en`             | `en`             | Fallback language if no user settings exist. Used for searching music.                                 |
| `DEFAULT_LOCATION` | `US`             | `US`             | Fallback location if no user settings exist. Used for searching music.                                 |
| `HOST_URL`         | `0.0.0.0`        | `0.0.0.0`        | The host IP to bind the server to.                                                                     |
| `HOST_PORT`        | `8960`           | `8960`           | The port to run the application on.                                                                    |
| `SECRET_KEY`       | `Auto-generated` | `Auto-generated` | Flask secret key. Auto-generated and saved if not provided.                                            |

> [!IMPORTANT]
> If you are using Docker or Podman, the `DATA_DIR` environment variable corresponds to the directory **inside** the container and must **always match the right side** of your volume mapping in `compose.yml`. For example, if you map `/home/me/Music:/app/data`, your `DATA_DIR` must be set to `/app/data`.

## Quick Start

You can use the interactive launcher script to quickly run AriaBox with or without a container engine:

1. Make the script executable:
   ```bash
   chmod u+x run.sh
   ```
2. Run the script:
   ```bash
   ./run.sh
   ```

### Using Docker or Podman

> > Make sure you have Docker or Podman installed.

The recommended way to run AriaBox is using a container engine. This handles all dependencies (including `ffmpeg`) and builds both the frontend and backend automatically. You can either pull the pre-built image directly from GitHub Container Registry, or build it locally from the source code.

#### Option A: Using the Pre-built Image (Recommended for most users)

1. First, create a directory wherever you want to store AriaBox's data and configuration. For example, in your home directory:
   ```bash
   mkdir ~/AriaBox
   cd ~/AriaBox
   ```
2. Create `compose.yml` file inside this directory. You can either download the [`compose.example.yml`](compose.example.yml) from the project root of this repository and rename it to `compose.yml`, or create a new `compose.yml` file and paste the contents of [`compose.example.yml`](compose.example.yml) into it.
3. Create `.env` file inside the same directory. Similarly, download the [`.env.example`](.env.example) from the project root and rename it to `.env`, or create a new `.env` file and copy the contents of [`.env.example`](.env.example) into it.
4. Open the `.env` file and update the values as needed. For example, you can set a custom `SECRET_KEY` or adjust the `DATA_DIR` if necessary.
5. Run the AriaBox:
   ```bash
   docker compose up -d
   # Or for Podman:
   podman compose up -d
   ```
6. Open your browser and navigate to `http://127.0.0.1:8960` (If you changed `HOST_PORT` variable, change `8960` to that instead).

#### Option B: Building from Source

1. Clone the repository and change directory into the project:
   ```bash
   git clone https://github.com/CheapNightbot/AriaBox.git && cd AriaBox
2. Copy the example environment variable `.env.example` file as `.env` to create your configuration:
   ```bash
   cp .env.example .env
   ```
3. (Optional) Open the newly created `.env` file and adjust any values as needed.
4. (Optional) Look at the `compose.yml` file and adjust any settings or volume mappings as needed.
5. Run the application:
   ```bash
   # For Docker:
   docker compose up --build -d

   # For Podman:
   podman compose up --build -d
   ```
6. Open your browser and navigate to `http://127.0.0.1:8960` (If you changed `HOST_PORT` variable, change `8960` to that instead).

> [!NOTE]
> **Rootless Docker/Podman Support:** AriaBox fully supports rootless Docker and Podman. If you are using rootless setup, please ensure you have configured the necessary user namespace variables in your `.env` file (as shown in `.env.example`) to resolve permission mapping issues between the host and the container.
>
> **Volume Mapping:** The default configuration maps a local `data` folder to the container's `/app/data` directory. AriaBox will automatically create this folder to store your runtime settings, auto-generated secret keys, and your organized music library.

### Running Directly

Running directly involves two steps: building the frontend first, and then running the backend, which serves the frontend's built files.

> [!IMPORTANT]
> **Prerequisite:** You **must** have `ffmpeg` installed and available in your system's PATH. Basic metadata tagging will function without it, but audio conversion and download features require `ffmpeg` to process the files.

1. Clone the repository and change directory into the project:
   ```bash
   git clone https://github.com/CheapNightbot/AriaBox.git && cd AriaBox
   ```
2. Copy the example environment variable `.env.example` file as `.env` to create your configuration:
   ```bash
   cp .env.example .env
   ```
3. (Optional) Open the newly created `.env` file and adjust any values as needed.
4. From the project root directory, install frontend dependencies & build the frontend:
   ```bash
   # Change directory to frontend
   cd frontend
   # Install dependencies
   pnpm install --frozen-lockfile --silent
   # Build frontend
   pnpm run build
   ```
5. Again, from the project root directory, start AriaBox:
   ```bash
   # Change directory to backend
   cd backend
   # Install dependencies
   uv sync
   # Run AriaBox ~
   uv run ariabox
   ```
6. Open your browser and navigate to `http://127.0.0.1:8960`.

## Development

For a seamless development experience, this project includes a fully configured `.devcontainer` directory.

> [!NOTE]
> The development workflow is **100% the same** whether you use the `.devcontainer` or your host machine! The *only* benefit of the devcontainer is that Python, `uv`, Node, `pnpm`, and `ffmpeg` are already pre-installed for you. You will still need to open two terminals and run the same commands.

**Terminal 1: Backend**
Change directory into the backend folder, install dependencies, and run the backend using Flask in debug mode:
```bash
cd backend
uv sync
uv run flask run --debug
# If developing inside a devcontainer or WSL, run this instead to listen on all hosts:
# uv run flask run --debug --host 0.0.0.0
```
The Flask development server will start on `http://127.0.0.1:5000`.

**Terminal 2: Frontend**
Change directory into the frontend folder, install dependencies, and run the Vite development server:
```bash
cd frontend
pnpm install
pnpm run dev
# If developing inside a devcontainer or WSL, run this instead to listen on all hosts:
# pnpm run dev --host 0.0.0.0
```
The Vite development server will start on `http://localhost:5173` and automatically proxy API requests to the backend running on port `5000`.

## Why me built AriaBox

me (secretly? sometime) sing cover songs, but the original song rarely have downloads for instrumental/karaoke version. on top of that, some only provide mp3 file and if you not know / notice, mp3 have this weird "feature" (not bug) where it adds little "padding" (? or really silence) at the beginning and end, which completely breaks timing (but converting to wav or any other format not have that)!!! so, me got so tired of sketchy, ad-filled websites just to download & convert audio and decided to create ArixBox ~

## Disclaimer

This project is developed for **educational and personal use only**.
- AriaBox is **not affiliated with, endorsed by, or sponsored by** Deezer, YouTube, Apple Music, or any other music service mentioned.
- All trademarks and service marks are the property of their respective owners.
- The author/creator is not responsible for any misuse of this software. Users are strongly encouraged to respect copyright laws and support artists by purchasing their music through official channels.
