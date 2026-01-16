from App import create_app
from App.models import db

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

app = create_app("ProductionConfig")

with app.app_context():
   #db.drop_all()
    db.create_all()
    
with app.app_context():
    if __name__ == '__main__':
        print("Registered routes:") #added to print registered routes for debugging
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    app.run(debug=app.config.get("DEBUG", False))
