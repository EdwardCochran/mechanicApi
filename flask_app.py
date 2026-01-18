from App import create_app
from App.models import db

app = create_app("ProductionConfig")
