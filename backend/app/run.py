from waitress import serve

from app import create_app


def run_server():
    app = create_app()
    host = app.config.get("HOST_URL", "0.0.0.0")
    port = app.config.get("HOST_PORT", 8960)

    print(f"AriaBox is running on http://{host}:{port} ٩(ˊᗜˋ*)و ♡")

    serve(
        app,
        host=host,
        port=port,
    )


if __name__ == "__main__":
    run_server()
