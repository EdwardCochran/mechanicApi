from App import create_app 
from App.models import db

app = create_app('DevelopmentConfig')

with app.app_context():
    db.create_all()
    
with app.app_context():
    if __name__ == '__main__':
        print("Registered routes:") #added to print registered routes for debugging
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    app.run(debug=True)

