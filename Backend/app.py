from flask import Flask, jsonify
from flask_cors import CORS
import os 
from models import db, Admin
from extensions import  mail
from dotenv import load_dotenv
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'resumes')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) 
    app.config['REPORTS_FOLDER'] = os.path.join(app.instance_path, 'reports')
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'alokmanawat6@gmail.com'
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_HOST_PASSWORD')   
    app.config['MAIL_DEFAULT_SENDER'] = 'alokmanawat6@gmail.com'
    app.config['ADMIN_REPORT_EMAIL'] = os.environ.get('ADMIN_REPORT_EMAIL', 'alokmanawat6@gmail.com')
    
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True   

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000",   
    ])

    db.init_app(app)
    mail.init_app(app)

    @app.route('/', methods=["GET"])
    def land():
        return jsonify({"success": True, "message": "API is running"}), 200

    from routes.admin   import admin_bp
    from routes.student import student_bp
    from routes.company import company_bp
    app.register_blueprint(admin_bp,   url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(company_bp, url_prefix='/company')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    with app.app_context():
        db.create_all()          
        _seed_admin(app)         

    return app

def _seed_admin(app):
   
    with app.app_context():
        username = os.environ.get("ADMIN_NAME","admin")
        password = os.environ.get("ADMIN_PASSWORD","admin123")
        if not Admin.query.filter_by(username=username).first():

            a = Admin(username=username)
            a.set_password(password)   
            db.session.add(a)
            db.session.commit()
           

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')