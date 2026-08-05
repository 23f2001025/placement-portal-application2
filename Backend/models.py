from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enroll_no = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(100),nullable=False)
    sem = db.Column(db.Integer,nullable=False)
    branch = db.Column(db.String(50),nullable=False)
    cgpa = db.Column(db.Float , default=0.0)
    is_blacklisted = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=False)

    applications  = db.relationship('Application', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Student {self.enroll_no} - {self.name}>'
    
class Company(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(150),nullable=False)
    website = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    officers = db.relationship('officers', backref='company', lazy=True)
    drives = db.relationship('CampusDrive',backref='company',lazy=True)
    is_validated = db.Column(db.Boolean , default = False)
    is_blacklisted  = db.Column(db.Boolean, default=False)
    registered_on   = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            "name":self.name,
            "website":self.website if self.website is  not None else None,
            "description":self.description,
            "registered_on":self.registered_on,
            "is_validated":self.is_validated
        }

class CampusDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title       = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    rounds_description = db.Column(db.Text,nullable=True)
    location        = db.Column(db.String(100), nullable=True)
    package_lpa     = db.Column(db.Float, nullable=True)       
    cutoff_cgpa        = db.Column(db.Float, default=0.0)
    allowed_branches= db.Column(db.String(255), nullable=True) 
    eligible_branches = db.relationship('EligibleBranch', backref='drive', lazy=True)
    deadline        = db.Column(db.DateTime, nullable=False)
    drive_date      = db.Column(db.DateTime, nullable=True)
    created_on      = db.Column(db.DateTime, default=datetime.now)   
    status          = db.Column(db.String(20), default='Pending')
    approved        = db.Column(db.Boolean, default=False)

    applications    = db.relationship('Application', backref='drive', lazy=True)
    interviews  = db.relationship('Interviews', backref='drive', lazy=True)



    def __repr__(self):
        return f'<Drive {self.job_title} by company {self.company_id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "rounds_description": self.rounds_description,
            "location": self.location,
            "package_lpa": self.package_lpa,
            "cutoff_cgpa": self.cutoff_cgpa,
            "allowed_branches": self.allowed_branches,
            "deadline": self.deadline,
            "drive_date": self.drive_date,
            "created_on": self.created_on,
            "status": self.status
        }


class Application(db.Model):
    __tablename__   = 'application'
    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id        = db.Column(db.Integer, db.ForeignKey('campus_drive.id'), nullable=False)
    applied_on      = db.Column(db.DateTime, default=datetime.utcnow)
    status          = db.Column(db.String(20), default='Applied')
    resume          = db.Column(db.String(100),nullable=True)
    __table_args__  = (db.UniqueConstraint('student_id', 'drive_id',
                                           name='unique_application'),)
    interview  = db.relationship('Interviews', backref='application', lazy=True)

    def __repr__(self):
        return f'<Application student={self.student_id} drive={self.drive_id} [{self.status}]>'
    
class officers(db.Model):
    __tablename__ = 'company_officers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_recruiter = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(30),nullable=False)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
class Announcements(db.Model):

    __tablename__  = 'Announcements'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime,default=datetime.now())
    text = db.Column(db.Text,nullable=True)
    headline = db.Column(db.Text,nullable=False)

class EligibleBranch(db.Model):
    __tablename__  = 'EligibleBranch'
    id = db.Column(db.Integer , primary_key=True)
    branch = db.Column(db.String(250),nullable=False)
    drive_id = db.Column(db.Integer , db.ForeignKey('campus_drive.id'),nullable=False)

class Interviews(db.Model):
    __tablename__ = 'Interviews'
    id = db.Column(db.Integer , primary_key=True)
    drive_id = db.Column(db.Integer , db.ForeignKey('campus_drive.id'),nullable=False)
    application_id = db.Column(db.Integer , db.ForeignKey('application.id'),nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Scheduled")
    feedback = db.Column(db.Text,nullable=True)
    panel_no = db.Column(db.Integer,default=0)

