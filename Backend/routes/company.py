from flask import Flask , Blueprint, render_template, request, redirect, flash , session
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask import jsonify
from flask import send_from_directory, current_app, abort
from datetime import datetime, timedelta
from task import send_interview_email
from auth import create_token , login_required


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
            token = create_token(company.id, "company")
            nam = company.name 
            return jsonify({"success":True,"message":"login successfull","token":token,"user_name":nam}),200
        
        return jsonify({"success":False,"message":"invalid credentials"}),200
    except Exception as e:

        return jsonify({"success":False,"message":f"something went wrong ! {e}"}),500
    

@company_bp.route('/dashboard',methods=["GET"])
@login_required('company')
def dashboard():
    try:
        usr_id = request.user_id
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
    usr_id = request.user_id
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
    usr_id = request.user_id
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
    usrid = request.user_id
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
        elif action == "select":
            app.status = "selected"
        elif action == "reject":
            app.status = "rejected"
        db.session.commit()
        return jsonify({"success":True,"message":"application updated"}),200
    drvs = CampusDrive.query.filter_by(company_id = usrid).all()
    applis = []
    shorted = []
    interviews = []
    accept = []
    for d in drvs:
        apps_pending = Application.query.filter_by(drive_id=d.id,status="Applied").all()
        apps_shortlisted = Application.query.filter_by(drive_id=d.id,status="shortlisted").all()
        apps_interview = Application.query.filter_by(drive_id=d.id,status="interview_scheduled").all()
        apps_selected = Application.query.filter_by(drive_id=d.id,status="selected").all()


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
        for a in apps_selected:
            st = Student.query.filter_by(id=a.student_id).first()
            accept.append({
                "id":a.id,
                "student_name":st.name,
                
                "drive_title":d.job_title,
                "status":a.status,
            })
        for a in apps_interview:
            st =  Student.query.filter_by(id=a.student_id).first()
            inter = Interviews.query.filter(Interviews.application_id == a.id , Interviews.drive_id == d.id).first()
            interviews.append({
                "id":a.id,
                "student_name":st.name,
                "drive_title":d.job_title,
                "date":inter.interview_date.strftime("%Y-%m-%d"),
                "start":inter.start_time.strftime("%H:%M"),
                "panel_no":inter.panel_no
            })
   
   
    print(type(applis),type(shorted),type(accept),type(interviews))
    user_name = comp.name
    return jsonify({"success":True,"applications":applis,"shortlisted":shorted,"user_name":user_name,"selected":accept,"interview":interviews}),200

@company_bp.route('/view-drives',methods=["GET"])
@login_required('company')
def viewDrives():
    try:
        usrid = request.user_id

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
        usrid = request.user_id
        if request.method == "PUT":
            data = request.get_json()
            
            dr = CampusDrive.query.filter_by(company_id =usrid,id=drive_id).first()
            if not dr:
                return jsonify({"success":False,"Message":"No such drive exist."})
            columns = [column.name for column in CampusDrive.__table__.columns]
            print(data)
            for c in columns:
                if c == "company_id":
                    continue 
                if c == "id":
                    continue 
                if c == "status":
                    continue 
                if c in data and c == "allowed_branches":
                    print("yes")
                    bs = [b.strip().upper() for b in data[c].split(",") if b.strip()]
                    for branch in bs:
                        if EligibleBranch.query.filter_by(drive_id=drive_id,branch=branch):
                            print("already")
                            continue 
                        elg = EligibleBranch(drive_id=drive_id.id,branch=branch)
                        db.session.add(elg)
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
        usrid = request.user_id
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
    

@company_bp.route('/schedule-interviews',methods=["POST"])
@login_required('company')
def schedule_interview():
    try:
        data = request.form

        date_str = data["interview_date"]
        drive_id = int(data["drive_id"])
        drive = CampusDrive.query.filter_by(id=drive_id).first()
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

        if end_dt <= start_dt:
            return jsonify({
                "success": False,
                "message": "end_time must be after start_time"
            }), 400

       
        one_inter = average + 5 + 5 + 10

        
        break_st = start_dt + timedelta(hours=4)
        break_en = start_dt + timedelta(hours=5)

       
        already_scheduled_app_ids = {
            i.application_id for i in Interviews.query.filter_by(drive_id=drive_id).all()
        }

        applis = Application.query.filter(
            Application.drive_id == drive_id,
            Application.status == "shortlisted"
        ).all()

        applis = [a for a in applis if a.id not in already_scheduled_app_ids]

       
        panel_times = [start_dt for _ in range(panels)]

        count = 0
        unscheduled = []
        send_mails = []

        for app in applis:
            scheduled = False

            
            for panel_num in sorted(range(panels), key=lambda p: panel_times[p]):
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

                
                app.status = "interview_scheduled"
                student = Student.query.filter_by(id=app.student_id).first()
                send_mails.append((
                    student.email, student.name, drive.job_title,
                    interview_date.strftime("%Y-%m-%d"),
                    st.time().strftime("%H:%M"),
                    panel_num + 1
                ))

                panel_times[panel_num] = interview_end
                count += 1
                scheduled = True
                break  

            if not scheduled:
                unscheduled.append(app.id)

        db.session.commit()
        for email_args in send_mails:
            send_interview_email.delay(*email_args)

        return jsonify({
            "success": True,
            "interviews_scheduled": count,
            "remaining": len(unscheduled),
            "unscheduled_application_ids": unscheduled
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def calculate_placement_stats(drives):

    overall = {
        "total_drives": len(drives),
        "total_applications": 0,
        "total_appeared": 0,        
        "total_shortlisted": 0,     
        "total_interview_scheduled": 0,
        "total_selected": 0,
        "total_rejected": 0,
        "shortlisted_but_rejected": 0,  
        "selection_percentage": 0.0,    
        "shortlist_percentage": 0.0,    
        "interview_to_selection_rate": 0.0, 
    }

    drive_breakdown = []

    for drive in drives:
        apps = drive.applications  

        total_apps = len(apps)
        selected = sum(1 for a in apps if a.status == "selected")
        rejected = sum(1 for a in apps if a.status == "rejected")
        interview_scheduled = sum(1 for a in apps if a.status == "interview_scheduled")
        shortlisted = sum(1 for a in apps if a.status == "shortlisted")

        
        shortlisted_or_beyond = sum(
            1 for a in apps
            if a.status in ("shortlisted", "interview_scheduled", "selected", "rejected")
        )

        
        shortlisted_then_rejected = sum(
            1 for a in apps if a.status == "rejected"
        )
        
        drive_total_appeared = total_apps  

        drive_stats = {
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "package_lpa": drive.package_lpa,
            "total_applications": total_apps,
            "shortlisted": shortlisted,
            "interview_scheduled": interview_scheduled,
            "selected": selected,
            "rejected": rejected,
            "shortlisted_but_rejected": shortlisted_then_rejected,
            "selection_percentage": round((selected / total_apps * 100), 2) if total_apps else 0.0,
        }
        drive_breakdown.append(drive_stats)

       
        overall["total_applications"] += total_apps
        overall["total_appeared"] += drive_total_appeared
        overall["total_shortlisted"] += shortlisted_or_beyond
        overall["total_interview_scheduled"] += interview_scheduled
        overall["total_selected"] += selected
        overall["total_rejected"] += rejected
        overall["shortlisted_but_rejected"] += shortlisted_then_rejected

    if overall["total_applications"] > 0:
        overall["selection_percentage"] = round(
            overall["total_selected"] / overall["total_applications"] * 100, 2
        )
        overall["shortlist_percentage"] = round(
            overall["total_shortlisted"] / overall["total_applications"] * 100, 2
        )

    interview_stage_total = (
        overall["total_interview_scheduled"]
        + overall["total_selected"]
        + overall["shortlisted_but_rejected"]
    )
    if interview_stage_total > 0:
        overall["interview_to_selection_rate"] = round(
            overall["total_selected"] / interview_stage_total * 100, 2
        )

    return {
        "overall": overall,
        "drive_breakdown": drive_breakdown
    }

import csv
import os
import time
from flask import current_app

def build_report_file(company_name, stats):
   
    filename = f"placement_report_{company_name.replace(' ', '_')}_{int(time.time())}.csv"
    filepath = os.path.join(current_app.config['REPORTS_FOLDER'], filename)

    overall = stats["overall"]
    drives = stats["drive_breakdown"]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

       
        writer.writerow([f"Placement Report - {company_name}"])
        writer.writerow([])
        writer.writerow(["Overall Summary"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Drives", overall["total_drives"]])
        writer.writerow(["Total Applications", overall["total_applications"]])
        writer.writerow(["Total Appeared", overall["total_appeared"]])
        writer.writerow(["Total Shortlisted", overall["total_shortlisted"]])
        writer.writerow(["Total Interview Scheduled", overall["total_interview_scheduled"]])
        writer.writerow(["Total Selected", overall["total_selected"]])
        writer.writerow(["Total Rejected", overall["total_rejected"]])
        writer.writerow(["Shortlisted but Rejected", overall["shortlisted_but_rejected"]])
        writer.writerow(["Selection Percentage (%)", overall["selection_percentage"]])
        writer.writerow(["Shortlist Percentage (%)", overall["shortlist_percentage"]])
        writer.writerow(["Interview-to-Selection Rate (%)", overall["interview_to_selection_rate"]])

        writer.writerow([])
        writer.writerow([])

        
        writer.writerow(["Drive-wise Breakdown"])
        writer.writerow([
            "Drive ID",
            "Job Title",
            "Package (LPA)",
            "Total Applications",
            "Shortlisted",
            "Interview Scheduled",
            "Selected",
            "Rejected",
            "Shortlisted but Rejected",
            "Selection Percentage (%)"
        ])

        for d in drives:
            writer.writerow([
                d["drive_id"],
                d["job_title"],
                d["package_lpa"],
                d["total_applications"],
                d["shortlisted"],
                d["interview_scheduled"],
                d["selected"],
                d["rejected"],
                d["shortlisted_but_rejected"],
                d["selection_percentage"],
            ])

    return filename

@company_bp.route('/export-report', methods=["POST"])
@login_required('company')
def export_report():
    try:
        company_id = request.user_id
        comp = Company.query.filter_by(id=company_id).first()
        if not comp:
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        drives = CampusDrive.query.filter_by(company_id=company_id).all()

        stats = calculate_placement_stats(drives)
        filename = build_report_file(comp.name, stats)

        return jsonify({
            "success": True,
            "message": "Report generated successfully",
            "report_url": f"/company/download-report/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@company_bp.route('/download-report/<filename>', methods=["GET"])
def download_report(filename):
    import os
    print(os.listdir(current_app.config['REPORTS_FOLDER']))
    return send_from_directory(
        current_app.config['REPORTS_FOLDER'],
        filename,
        as_attachment=True
    )