from flask import Flask , Blueprint, render_template, request, redirect, flash , session ,current_app , jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import *
from werkzeug.utils import secure_filename
import os 

from flask import send_from_directory, current_app, abort

from auth import login_required , create_token

student_bp = Blueprint('student', __name__)

student_table = {
    "0103IS231020":{
        "Name":"XYZ Sharma",
        "Class":"BS-A1",
        "Branch":"CSE",
        "Sem":6,
        "cgpa":7.96
    },
    "0103IS231550":{
        "Name":"XYZ Verma",
        "Class":"BS-A1",
        "Branch":"DS",
        "Sem":6,
        "cgpa":6.9
    },
    "0103IS231560":{
        "Name":"Sushant pathak",
        "Class":"BS-A1",
        "Branch":"IOT",
        "Sem":6,
        "cgpa":7.5
    },
    "0103IS231570":{
        "Name":"Sushant srivastava",
        "Class":"BS-A1",
        "Branch":"IOT",
        "Sem":6,
        "cgpa":8.0
    }

}
@student_bp.route('/register',methods=['POST','GET'])
def student_register():
    try:
        if request.method == "POST":
            data = request.get_json()
            enroll_no = data.get("enroll_no","")
            if not enroll_no:
                return jsonify({"success":False,"message":"Invalid Enrollment number , check you student identity"}),200
            stb = Student.query.filter_by(enroll_no=enroll_no).first()
            if stb:
                return jsonify({"success":False,"message":"Already Registered, Please login"}),200
            pass1 = data.get("password1","")
            pass2 = data.get("password2","")
            mail = None 
            if "mail_id" in data:
                mail = data.get("mail_id")
            if not pass1:
                return jsonify({"success":False,"message":"Enter password first"}),200
            if pass1 != pass2:
                return jsonify({"success":False,"message":"Both the passwords should be same"}),200
            if enroll_no not in student_table:
                return jsonify({"success":False,"message":"Invalid enrollment number , check credentials"}),200
            std = student_table[enroll_no]
            print(std)
            usr = Student(enroll_no=enroll_no,name=std["Name"],sem=std["Sem"],branch=std["Branch"],email=mail,cgpa=std["cgpa"])
            usr.set_password(pass1)
            db.session.add(usr)
            db.session.commit()
            return jsonify({"success":True,"message":"registered successfully"}),200
        return jsonify({"success":False,"message":"GET method not supported for this API"}),200
    except Exception as e:
        return jsonify({"success":False,"message":f"something went wrong ! {e}"}),500

@student_bp.route('/login',methods=["POST","GET"])
def student_login():
    try:
        if request.method == "POST":
            data = request.get_json()
            enroll_no = data.get("enroll_no","")
            passw = data.get("password","")
            if not enroll_no or not passw:
                return jsonify({"success":False,"message":"Enter enroll_no and password"}),200
            usr = Student.query.filter_by(enroll_no=enroll_no).first()
            if not usr or not usr.check_password(passw):
                return jsonify({"success":False,"message":"Invalid credentials"}),200
            token = create_token(usr.id,"student")
            nam = usr.name 
            return jsonify({"success":True,"message":"login successfull","token":token,"user_name":nam}),200
        return jsonify({"success":False,"message":"GET method not supported for this API"}),200
    except Exception as e:
        return jsonify({"success":False,"message":f"{e}"}),500
    
@student_bp.route('/dashboard',methods=["GET"])
@login_required('student')
def dashboard():
    try:
        stid = request.user_id
        st = Student.query.filter_by(id=stid).first()
        if not st:
            return jsonify({"success":False,"message":"Unauthorized Access"}),401
        applications = Application.query.filter_by(student_id=stid).all()
        camp_drives = CampusDrive.query.filter(
            CampusDrive.deadline > datetime.now(),
            CampusDrive.status == 'Applications Open' 
        ).all()
        announce = Announcements.query.order_by(Announcements.date.desc()).limit(3).all()
        announces = []
        for a in announce:
            announces.append({
                "Title":a.headline,
                "text":a.text,
                "date":a.date 
            })
        drives = []
        for d in camp_drives:
            drives_obj = {}
            cmp = Company.query.filter_by(id=d.company_id).first()
            cmp_name = cmp.name 
            drives_obj["company_name"] = cmp_name
            drives_obj["job_description"] = d.job_description
            drives_obj["job_title"] = d.job_title
            drives_obj["deadline"] = d.deadline 
            drives_obj["drive_id"] = d.id 
            drives.append(drives_obj)
        
        apps = []
        for ap in applications:
            dr = CampusDrive.query.filter_by(id = ap.drive_id).first()
            apps.append({
                "job_title":dr.job_title,
                "drive_id":ap.drive_id,
                "status":ap.status,
                "applied":ap.applied_on 
            })

        user_name=st.name
        return jsonify({"success":True,"drives":drives,"applications":apps,"announcements":announces,"user_name":user_name}),200
    except Exception as e:
        return jsonify({"success":False,"message":f"{e}"}),500
    
@student_bp.route('/view-applications',methods=["GET"])
@login_required('student')
def application():
    usr_id = request.user_id
    st = Student.query.filter_by(id=usr_id).first()
    if not st:
        return jsonify({"success":False,"message":"Unauthorizedd Access"}),401
    apps = Application.query.filter_by(student_id=st.id).all()
    applis = []
    inters = []
    for a in apps:
        d = CampusDrive.query.filter_by(id=a.drive_id).first()
        interviews = Interviews.query.filter_by(application_id=a.id)
        if interviews:
            for i in interviews:
                inters.append({
                    "drive_title":d.job_title,
                    "status":a.status,
                    "date":i.interview_date.strftime("%Y-%m-%d"),
                    "start":i.start_time.strftime("%H:%M"),
                })

        applis.append({
            "resume":a.resume,
            "id":a.id,
            "drive_id":a.drive_id,
            "drive_title":d.job_title,
            "status":a.status,
            "package":d.package_lpa,
            "offer_letter": a.offer_letter if a.offer_letter else None
        })
   
    
    
    user_name=st.name
    return jsonify({"success":True,"applications":applis,"user_name":user_name,"interviews":inters}),200

@student_bp.route('/apply',methods=["POST","GET"])
@login_required('student')
def apply():
    usrid = request.user_id
    st = Student.query.filter_by(id=usrid).first()
    if not st:
        return jsonify({"success":False,"message":"Unauthorized Access,"}),401
    if request.method == "POST":
        data = request.form 
        file = request.files.get('resume')
       
        drive_id = data["drive_id"]
        
        filename = None
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(f"{usrid}_{drive_id}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            return jsonify({"success":False,"message":"Please upload a valid PDF resume"}),200
        
        
        existing = Application.query.filter_by(student_id=usrid, drive_id=drive_id).first()
        if existing:
            return jsonify({"success":False,"message":"Already applied to this drive"}),200
        drive = CampusDrive.query.filter_by(id=drive_id).first()
        if drive.approved == False or drive.status != "Applications Open":
            return jsonify({"success":False,"message":"Drive is not available"})

        elg = [eb.branch for eb in drive.eligible_branches]
        elg2 = [b.strip().upper() for b in drive.allowed_branches.split(",") if b.strip()]
        print(elg)
        
       
        if st.is_blacklisted == True:
            return jsonify({"success":False,"message":"You are BlackListed From the Institue"}),200
        if elg and (st.branch.upper()  not in elg) and ("ALL" not in elg) and (st.branch.upper() not in elg2):
            return jsonify({"success":False,"message":"Your Branch is not eligible for this drive"}),200
        if st.cgpa < drive.cutoff_cgpa:
            return jsonify({"success":False,"message":"Your are not eligible for this drive because of cgpa constraints by company"}),200
       
        app = Application(student_id=usrid, drive_id=drive_id, resume=filename)
        db.session.add(app)
        db.session.commit()
        return jsonify({"success":True,"message":"Applied successfully!"}),200
    user_name=st.name
    drvs = CampusDrive.query.filter_by(status="Applications Open").all()
    drives = []
    for d in drvs:
        comp = d.company 
        app = Application.query.filter_by(drive_id=d.id,student_id=st.id).first()
        ststs = "Not Applied"
        if app:
            ststs = app.status 
        drives.append({
            "drive_id":d.id,
            "job_title":d.job_title,
            "company":comp.name,
            "package":d.package_lpa,
            "status":ststs
        })
    return jsonify({"success":True,"drives":drives,"user_name":user_name}),200


@student_bp.route('/profile',methods=["GET","POST"])
@login_required('student')
def profile():
    usrid = request.user_id
    st = Student.query.filter_by(id=usrid).first()
    if not st:
        return jsonify({"success":False,"message":"Unauthorized Access"}),401
    if request.method == "POST":
        data = request.form 
        mail = data.get("email")
        if not mail:
            return jsonify({"success":False,"message":"Please enter a valid email address"}),200
        st.email = mail 
        db.session.commit()
        return jsonify({"success":True,"message":"profile updated"}),200
    student = {
        "name":st.name,
        "branch":st.branch,
        "sem":st.sem,
        "cgpa":st.cgpa,
        "is_blacklisted":st.is_blacklisted,
        "email":st.email if st.email is not None else None 
    }
    user_name=st.name
    return jsonify({"success":True,"student":student,"user_name":user_name}),200



@student_bp.route('/resume/<int:drive_id>',methods=["GET"])
@login_required('student')
def get_resume(drive_id):

   
    student_id = request.user_id 
    std = Student.query.filter_by(id=student_id).first()
    if not std:
        return jsonify({"success":False,"message":"Unathourized access"}),401

    application = Application.query.filter_by(
        drive_id=drive_id,
        student_id=student_id
    ).first()

    if not application or not application.resume:
        abort(404, description="Resume not found")

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        application.resume,
        as_attachment=False  
    )

@student_bp.route('/offer-letter/<int:app_id>', methods=["GET"])
@login_required('student')
def view_offer_letter_student(app_id):
    student_id = request.user_id
    application = Application.query.filter_by(id=app_id, student_id=student_id).first()
    if not application or not application.offer_letter:
        return jsonify({"success": False, "message": "Not found"}), 404

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], application.offer_letter)