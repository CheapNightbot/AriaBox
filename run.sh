#!/bin/bash

echo "Welcome to the AriaBox Launcher (˶˃ ᵕ ˂˶).ᐟ.ᐟ"
echo "==========================================="
echo "How would you like to run the application?"
echo "1) With Docker / Podman (Recommended)"
echo "2) Without Docker (Local Production Mode)"
echo "3) No thank you, just exit"
echo
read -p "Enter your choice (1-3): " choice

case $choice in
  1)
    echo
    echo "Starting containerized environment... ☆⌒(ゝ。∂)"
    # Smart check: use podman if available, otherwise fallback to docker
    if command -v podman &> /dev/null; then
        podman compose up --build -d
    else
        docker compose up --build -d
    fi
    ;;
  2)
    echo
    echo "Building Frontend... ☆⌒(ゝ。∂)"
    cd frontend && pnpm install --frozen-lockfile --silent && pnpm run build && cd ..

    echo
    echo "Preparing Backend... (๑'ᵕ'๑)⸝*"
    cd backend && uv sync

    echo
    echo "Starting the application! ٩(ˊᗜˋ*)و"
    uv run ariabox
    ;;
  3)
    echo
    echo "Okie, bye! (✿ᴗ͈ˬᴗ͈)⁾⁾"
    exit 0
    ;;
  *)
    echo
    echo "Invalid choice. Please run the script again. “(ノ _ <,, )"
    exit 1
    ;;
esac
