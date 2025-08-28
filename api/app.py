from app_factory.create_app import create_app  # or just from this file if inline

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
