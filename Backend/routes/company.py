from flask import Flask , Blueprint, render_template, request, redirect, flash , session
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask import jsonify
from utils import login_required
from flask import send_from_directory, current_app, abort
from datetime import datetime, timedelta


company_bp = Blueprint('company', __name__)

    
@company_bp.route('/register',methods=["POST"])
def company_register():
        try:
            data = request.get_json()
            company_name = data["company_name"]
            comp = Company.query.filter_by(name=company_name).first()
            if comp:
                msg = "company with this registered name already exist"
                return jsonify({"success":False,"message":msg}),200
            
            
            officers_mail = data["hr_email"]
            officers_name = data["hr_name"]                
            pass1 = data["password1"]
           
            pass2 = data["password2"]
            if pass1 != pass2:
                msg = "Both the passwords should be same","error"
                return jsonify({"success":False,"message":msg}),200
            comp = Company(name=company_name)
            comp.set_password(pass1)
            
            db.session.add(comp)
            db.session.flush()   
            off = officers(email=officers_mail, name=officers_name, company_id=comp.id, is_recruiter=True)
            db.session.add(off)
            db.session.commit()
            return jsonify({"success":True,"message":"company regietered"}),200
        except Exception as e:
            
            return jsonify({"success":False,"message":f"something went wrong ! {e}"}),500
        
    

@company_bp.route('/login',methods=["POST"])
def company_login():
    try:
        data = request.get_json()
        company_id = data["company_name"]
        password = data.get("password","")
        if not password.strip():
            return jsonify({"success":False,"message":"Password required"})
        passw = data["password"]
        company = Company.query.filter_by(name=company_id).first()
        if not company:
            
            return jsonify({"success":False,"message":"company not found"}),404
        if company.is_validated == False:
            
            return jsonify({"success":False,"message":"Institute did not accepted yet"}) , 200
        if company.check_password(passw):
            session['role'] = 'company'
            session['user_id'] = company.id
            return jsonify({"success":True,"message":"login successfull"}),200
        
        return jsonify({"success":False,"message":"invalid credentials"}),200
    except Exception as e:

        return jsonify({"success":False,"message":f"something went wrong ! {e}"}),500
    

@company_bp.route('/dashboard',methods=["GET"])
@login_required('company')
def dashboard():
    try:
        usr_id = session["user_id"]
        cmp = Company.query.filter_by(id=usr_id).first()
        if not cmp:
            return jsonify({"success":False,"message":"company not found"}),404
       
        drives = CampusDrive.query.filter_by( company_id = usr_id).all()
        drives_list = []
        student_apps = []
        for d in drives:
            drives_obj = {}
            apps = Application.query.filter_by(drive_id = d.id).all()
            drives_obj["Name"] = d.job_title
            drives_obj["drive_id"] = d.id 
            for ap in apps:
                st = ap.student 
                student_apps.append({
                    "name":st.name,
                    "branch":st.branch,
                    "cgpa":st.cgpa,
                    "status":ap.status,
                })
            drives_list.append(drives_obj)
        user_name = cmp.name
        return jsonify({"success":True,"drives":drives_list,"student_applications":student_apps,"user_name":user_name}),200
    except Exception as e:
        return jsonify({"success":False,"message":f"{e}"}),500

@company_bp.route("/drive",methods=["GET"])
def drive_page():

    drive_id = request.args.get("id")
    drive_obj = CampusDrive.query.filter_by(id = drive_id).first()
    if not drive_obj:
        return jsonify({"success":False,"message":"drive not found"}),404
    drive = drive_obj.to_dict()
    return jsonify({"success":True,"drive":drive}),200


@company_bp.route('/create-drive',methods=["GET","POST"])
@login_required('company')
def create_placement():
    usr_id = session["user_id"]
    comp = Company.query.filter_by(id = usr_id).first()
    if not comp:
        return jsonify({"success":False,"message":"Invalida credentials"}),200
    if request.method == "POST":
        
        data = request.form
        job_title       = data["job_title"]
        job_description = data["description"]
        rounds_description = data["Round-Description"]
        location        = data["location"]
        package_lpa     = float(data["package"])  
        cutoff_cgpa        = float(data["cutoff-cgpa"])
        allowed_branches= data["branches"]
        deadline_str        = data["deadline"]
        drive_date_str      = data["drive-date"]
       
        drv = CampusDrive.query.filter_by(company_id = comp.id,job_title=job_title).first()
        if drv:
            
            return jsonify({"success":False,"message":"Drive already  created  , If you want to create new one , delete the old one"}),200
        deadline = datetime.strptime(deadline_str, "%d-%m-%Y")
        drive_date = datetime.strptime(drive_date_str, "%d-%m-%Y")

        obj = CampusDrive(
            company_id=usr_id,
            job_title=job_title,
            job_description=job_description,
            rounds_description=rounds_description,
            allowed_branches=allowed_branches,
            location = location,
            package_lpa=package_lpa,
            cutoff_cgpa = cutoff_cgpa,
            deadline=deadline,
            drive_date=drive_date
        )
        db.session.add(obj)
        db.session.flush()
        if allowed_branches:
            bs = [b.strip().upper() for b in allowed_branches.split(",") if b.strip()]
            for branch in bs:
                elg = EligibleBranch(drive_id=obj.id,branch=branch)
                db.session.add(elg)

       
        db.session.commit()
        return jsonify({"success":True,"message":"drive created"}),200
    user_name = comp.name
    drives = CampusDrive.query.filter_by( company_id = usr_id).all()
    drives_list = []
    student_apps = []
    for d in drives:
        drives_obj = {}
        apps = Application.query.filter_by(drive_id = d.id).all()
        drives_obj["Name"] = d.job_title
        drives_obj["drive_id"] = d.id 
        for ap in apps:
            st = ap.student 
            student_apps.append({
                "name":st.name,
                "branch":st.branch,
                "cgpa":st.cgpa,
                "status":ap.status,
            })
        drives_list.append(drives_obj)

    return jsonify({"success":True,"drives":drives_list,"student_applications":student_apps,"user_name":user_name}),200
    

@company_bp.route('/profile',methods=["GET","POST"])
@login_required('company')
def profile():
    usr_id = session['user_id']
    comp = Company.query.filter_by(id=usr_id).first()
    if not comp:
        return jsonify({"success":False,"message":"Unauthorized Access"}),200
    if request.method == "POST":
        data = request.form 
        if "description" in data:
            des = data["description"]
            comp.description = des 
       
        if "website" in data:
            web = data["website"]
            comp.website = web 
        db.session.commit()
        return jsonify({"success":True,"message":"profile updated"}),200
    
    comp = Company.query.filter_by(id=usr_id).first()
    user_name = comp.name
    data = comp.to_dict()
    return jsonify({"success":True,"company":data,"user_name":user_name}),200


@company_bp.route('/applications',methods=["GET","POST"])
@login_required('company')
def student_applications():
    usrid = session["user_id"]
    comp = Company.query.filter_by(id = usrid).first()
    if not comp:
        return jsonify({"success":False,"message":"Unauthorized Access"}),401 
    if request.method == "POST":
        data = request.form
        app_id = data["application_id"]
        app = Application.query.filter_by(id = app_id).first()
        action = data["action"]
        if action == "shortlist":
            app.status = "shortlisted"
        elif action == "remove":
            db.session.delete(app)
        db.session.commit()
        return jsonify({"success":True,"message":"application updated"}),200
    drvs = CampusDrive.query.filter_by(company_id = usrid).all()
    applis = []
    shorted = []
    for d in drvs:
        apps_pending = Application.query.filter_by(drive_id=d.id,status="Applied").all()
        apps_shortlisted = Application.query.filter_by(drive_id=d.id,status="shortlisted").all()


        for a in apps_pending:
            st = Student.query.filter_by(id = a.student_id).first()

            applis.append({
                "id":a.id,
                "student_name":st.name,
                "branch":st.branch,
                "student_id":st.id,
                "drive_title":d.job_title,
                "status":a.status,
                "cgpa":st.cgpa,
                "drive_id":d.id ,
                "resume":a.resume if a.resume is not None else None 
            })
        for a in apps_shortlisted:
            st = Student.query.filter_by(id=a.student_id).first()
            shorted.append({
                "id":a.id,
                "student_name":st.name,
                "branch":st.branch,
                "drive_title":d.job_title,
                "status":a.status,
                "cgpa":st.cgpa,
                "student_id":st.id,
                "drive_id":d.id, 
            })
    user_name = comp.name
    return jsonify({"success":True,"applications":applis,"shortlisted":shorted,"user_name":user_name}),200

@company_bp.route('/view-drives',methods=["GET"])
@login_required('company')
def viewDrives():
    try:
        usrid = session["user_id"]

        drvs = CampusDrive.query.filter_by(company_id=usrid)
        drives = []
        for d in drvs:
            closed = d.status == "Applications Closed"
            drives.append({
                "drive_id":d.id,
                "Title":d.job_title,
                "status":d.status,
                "applications_closed":closed
            })
        return jsonify({"success":True,"drives":drives}),200
    except Exception as e:
        return jsonify({"success":False,"Message":e}),500
    

@company_bp.route('/edit-drives/<int:drive_id>',methods=["PUT","DELETE","POST"])
@login_required('company')
def editDrives(drive_id):
    try:
        usrid = session["user_id"]
        if request.method == "PUT":
            data = request.get_json()
            
            dr = CampusDrive.query.filter_by(company_id =usrid,id=drive_id).first()
            if not dr:
                return jsonify({"success":False,"Message":"No such drive exist."})
            columns = [column.name for column in CampusDrive.__table__.columns]
            for c in columns:
                if c == "company_id":
                    continue 
                if c == "id":
                    continue 
                if c == "status":
                    continue 
                if c in data:
                    setattr(dr, c, data[c])
           
            db.session.commit()
            return jsonify({"success":True,"Message":"Drive updated successfully"}),200
        if request.method == "DELETE":
            
            drv = CampusDrive.query.filter_by(company_id=usrid,id=drive_id).first()
            if not drv:
                return jsonify({"success":False,"message":"No such drive exist."})
            db.session.delete(drv)
            db.session.commit()
            return jsonify({"success":True,"message":"Drive deleted successfully."}),204
        if request.method == "POST":
            
            drv = CampusDrive.query.filter_by(company_id=usrid,id=drive_id).first()
            if not drv:
                return jsonify({"success":False,"message":"No such drive exist."})

            if drv.approved == False:
                return jsonify({"success":False,"message":"Drive not approved by college"})
            drv.status = "Applications Closed"
            
            db.session.commit()
            return jsonify({"success":True,"message":"Applications closed"})
        return jsonify({"success":False,"message":"BAD Request."})
    except Exception as e:
        return jsonify({"success":False,"message":f"something went wrong {e}"}),500


@company_bp.route('/edit-drives/open/<int:drive_id>',methods=["PUT"])
@login_required('company')
def openDrive(drive_id):
    try:
        usrid = session["user_id"]
        drv = CampusDrive.query.filter_by(company_id=usrid,id=drive_id).first()
        if not drv:
            return jsonify({"success":False,"message":"No such drive exist."})
        if drv.approved == False:
            return jsonify({"success":False,"message":"Drive not approved by college"})
        drv.status = "Applications Open"
        
        db.session.commit()
        return jsonify({"success":True,"message":"Applications Opened"})
        
    except Exception as e:
        return jsonify({"success":False,"message":f"something went wrong {e}"}),500
    

@company_bp.route('/student-resume/<int:student_id>/<int:drive_id>',methods=["GET"])
@login_required('company')
def student_resume(student_id,drive_id):
    try:
        app = Application.query.filter_by(student_id=student_id,drive_id=drive_id).first()
        if not app:
            return jsonify({"success":False,"message":"No drive or studnt found"})
        
        return send_from_directory(
                current_app.config['UPLOAD_FOLDER'],
                app.resume,
                as_attachment=False  
            )
    except Exception as e:
        return jsonify({"success":False,"message":f"{e}"}),500
    


def schedule_interview():
    try:
        data = request.form

        date_str = data["date"]
        drive_id = int(data["drive_id"])

        start_str = data["start_time"]
        end_str = data["end_time"]

        average = int(data["average_time"])
        panels = int(data["number_of_panels"])

        
        interview_date = datetime.strptime(
            date_str, "%Y-%m-%d"
        ).date()

        start_dt = datetime.strptime(
            f"{date_str} {start_str}",
            "%Y-%m-%d %H:%M"
        )

        end_dt = datetime.strptime(
            f"{date_str} {end_str}",
            "%Y-%m-%d %H:%M"
        )

       
        one_inter = average + 10 + 10 + 10

       
        break_st = start_dt + timedelta(hours=4)
        break_en = start_dt + timedelta(hours=5)

       
        applis = Application.query.filter(
            Application.drive_id == drive_id,
            Application.status == "shortlisted"
        ).all()

        
        panel_times = [start_dt for _ in range(panels)]

        count = 0

        for app in applis:

            
            panel_num = min(
                range(panels),
                key=lambda p: panel_times[p]
            )

            st = panel_times[panel_num]

           
            if break_st <= st < break_en:
                st = break_en

            interview_end = st + timedelta(minutes=one_inter)

            
            if st < break_st and interview_end > break_st:
                st = break_en
                interview_end = st + timedelta(minutes=one_inter)

            
            if interview_end > end_dt:
                continue

            interview = Interviews(
                drive_id=drive_id,
                application_id=app.id,
                start_time=st.time(),
                end_time=interview_end.time(),
                interview_date=interview_date,
                panel_no=panel_num + 1,
                status="Scheduled"
            )

            db.session.add(interview)

            count += 1

           
            panel_times[panel_num] = interview_end

        db.session.commit()

        return jsonify({
            "success": True,
            "Interviews scheduled": count,
            "remaining": len(applis) - count
        })

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


