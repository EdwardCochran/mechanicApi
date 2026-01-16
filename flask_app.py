from App import create_app
from App.models import db

app = create_app("ProductionConfig")

if __name__ == "__main__":
    # Only for local/dev runs
    with app.app_context():
        db.create_all()

    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.endpoint}")

    app.run(debug=app.config.get("DEBUG", False))
