from flask import Flask
from config import Config
from models import db
from api_routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return 'Farmer Market API'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
