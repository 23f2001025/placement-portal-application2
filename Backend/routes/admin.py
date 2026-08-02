from flask import Flask , Blueprint, render_template, request, redirect, flash , session
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask import jsonify
from utils import login_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login',methods=["POST"])
def admin_login():
    if session.get('role') == 'admin':
        print("yha se")
        return jsonify({
            "success": True,
            "message": "Already logged in"
        }), 200
   
    try:
        print("aaya")
        data = request.get_json() 
        username = data["username"]
        if not "password" in data:
            return jsonify({
                "success":False,
                "message":"password not found"
            }),400
        passw = data["password"]
        admn = Admin.query.filter_by(username=username).first()
        if admn and admn.check_password(passw):
            session['role'] = 'admin'
            session['user_id'] = admn.id
            return jsonify({
                "success":True,
                "message":"User Logged In"
            }),200
        
        return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),401
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"something went wrong {e}"
        }),500
    


@admin_bp.route('/dashboard',methods=["GET"])
@login_required('admin')  
def dashboard():
    try:
        print("aaya")
        stds = Student.query.count()
        drives = CampusDrive.query.filter(
            CampusDrive.deadline > datetime.now(),
            CampusDrive.status == 'Approved'
        ).all()

        pending_drives  = CampusDrive.query.filter(
            CampusDrive.status == 'Pending'
        ).all()

        on_going_drives = []
        for d in drives:
            on_going_drives.append({
                "Title":d.job_title,
                "id":d.id
            })
        upcoming = []
        for d in pending_drives:
            upcoming.append({
                "Title":d.job_title,
                "id":d.id 
            })
       
        comps_count  =  Company.query.count()
        not_approved = Company.query.filter_by( is_validated = False).count()
        user_name = 'admin'
        
        return jsonify({
            "success":True,
            "ongoing_drives":on_going_drives,
            "upcoming_drives":upcoming,
            "company_count":comps_count,
            "not_approved":not_approved,
            "user_name":user_name,
            "message":"success",
            "student_count":stds,
        }),200
    except Exception as e:
        
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500
    
   
@admin_bp.route('/managecompany/approveCompany',methods=["POST"])
@login_required('admin')
def approve_company():
    try:
        data = request.get_json()
        comp_id = data["company_id"]

        comps = Company.query.filter_by(id = comp_id).first()
        if not comps:
            return jsonify({"success":False,"message":"Company not found"})
        
        comps.is_validated = True 
    
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"company approved"
        }),200
    except Exception as e:
         return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

   
@admin_bp.route('/managecompany/blacklist',methods=["POST"])
@login_required('admin')
def blacklist_company():
    try:
        data = request.get_json()
        comp_id = data["company_id"]
        comps = Company.query.filter_by(id = comp_id).first()
        comps.is_blacklisted = True 
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"company blacklisted"
        }),200
    except Exception as e:
         return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

   
@admin_bp.route('/managecompany/searchCompany',methods=["POST"])
@login_required('admin')
def search_company():
    try:
        data = request.get_json()
        sid = data["search_id"]
        comps = Company.query.filter(Company.name.ilike(f"%{sid}%")).all()
        sr = []
        if comps:
            for comp in comps:
                drvs = len(CampusDrive.query.filter_by(company_id =comp.id).all())
                sr.append({
                    "name":comp.name,
                    "drives":drvs,
                })
       
        print(sr)
        return jsonify({
            "success":True,
            "search_result":sr 
        })
    except Exception as e:
         return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500 


    
@admin_bp.route('/managecompany',methods=["GET"])
@login_required('admin')
def manage_companies():
    try:            
        user_name = 'admin'
        pen_comp = Company.query.filter_by( is_validated = False,is_blacklisted=False).all()
        approved_comp = Company.query.filter_by( is_validated = True,is_blacklisted=False).all()
        approved_comps = []
        pending_comps = []
        for d in approved_comp:
            off =  officers.query.filter_by(company_id = d.id,is_recruiter=True).first()
            approved_comps.append({
                "name":d.name,
                "website":d.website,
                "hr":off.name if off else "N/A",
                "email":off.email if off else "N/A"
            })
        for d in pen_comp:
            off =  officers.query.filter_by(company_id = d.id,is_recruiter=True).first()
            pending_comps.append({
                "id":d.id,
                "name":d.name,
                "website":d.website,
                "hr":off.name if off else "N/A",
                "email":off.email if off else "N/A", 
            })
        return jsonify({
            "success":True,
            "approved_companies":approved_comps,
            "pending_companies":pending_comps,
            "user_name":user_name
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":"something went wrong {e}"
        }),500

@admin_bp.route('/managestudents/blacklist',methods=["POST"])
@login_required('admin')
def blacklist_student():
    try:
        data = request.get_json()
        student_id = data["student_id"]
        std = Student.query.filter_by(id=student_id).first()
        std.is_blacklisted = True 
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"student blacklisted"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

@admin_bp.route('/managestudents/remove',methods=["DELETE"])
@login_required('admin')
def remove_student():
    try:
        data = request.get_json()
        student_id = data["student_id"]
        std = Student.query.filter_by(id=student_id).first()
        if not std:
            return jsonify({
                "success":False,
                "message":"Student not found"
            }),404
        db.session.delete(std)
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"student removed"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

@admin_bp.route('/managestudents/announcement',methods=["POST"])
@login_required('admin')
def make_announce():
    try:
        data = request.form 
        print(data)
        title = data["headline"]
        text = data["text"]
        anounce = Announcements(
            headline=title,
            text=text
        )
        db.session.add(anounce)
        db.session.commit()
        
        return jsonify({
            "success":True,
            "message":"Announcement made"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

@admin_bp.route('/managestudents/delete-announcement',methods=["DELETE"])
@login_required('admin')
def delete_announce():
    try:
        data = request.get_json()
        announce_id = data["announce_id"]
        an = Announcements.query.filter_by(id = announce_id).first()
        db.session.delete(an)
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"Announcement deleted"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

@admin_bp.route('/managestudents/search-student',methods=["POST"])
@login_required('admin')
def search_student():
    try:
        sr = []
        data = request.form 
       
        search_by = data["search_by"]
        sid = data["search_id"]
        print(sid)
        st = None
        if search_by == "name":
            st = Student.query.filter(Student.name.ilike(f"%{sid}%")).all()
            print(st)
        else:
            st = Student.query.filter_by(enroll_no=sid).all()
        
        if st is not None:
            for s in st:
                sr.append({
                    "name":s.name,
                    "sem":s.sem,
                    "branch":s.branch,
                    "email":s.email,
                    "cgpa":s.cgpa
                })
        return jsonify({
            "success":True,
            "search_result":sr
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500




@admin_bp.route('/managestudents',methods=["GET"])
@login_required('admin')  
def manage_students():
    try:
        announce = Announcements.query.order_by(Announcements.date.desc()).limit(3).all()
        announces = []
        for a in announce:
            announces.append({
                "Title":a.headline,
                "text":a.text,
                "date":a.date,
                "id":a.id  
            })
        sts = Student.query.filter_by(is_blacklisted = False).all()
        apps   = Application.query.filter_by(status="shortlisted").all()
        reg_students = []
        for st in sts:
            reg_students.append({
                "Name":st.name,
                "Branch":st.branch,
                "Enroll":st.enroll_no,
                "cgpa":st.cgpa,
                "email":st.email,
                "id":st.id 
            })
        placed_stds = []
        for aps in apps:
            drv = CampusDrive.query.filter_by(id=aps.drive_id).first()
            
            st = Student.query.filter_by(id=aps.student_id).first()
            placed_stds.append({
                "Name":st.name,
                "Branch":st.branch,
                "enroll_no":st.enroll_no,
                "cgpa":st.cgpa,
                "email":st.email,
                "drive":drv.job_title,
                "drive_id":drv.id,
                "package":drv.package_lpa 
            })

        user_name = 'admin'
        return jsonify({
            "success":True,
            "registered_students":reg_students,
            "placed_students":placed_stds,
            "announcements":announces,
            "user_name":user_name
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500
            

@admin_bp.route('/placement-drives/accept-drive',methods=["POST"])
@login_required('admin')  
def approve_drive():
    try:
        print("hello")
        data = request.form 
        dr_id = int(data["drive_id"])
        print(dr_id)
        drv = CampusDrive.query.filter_by(id = dr_id).first()
        if not drv:
            return jsonify({
                "success":False,
                "message":"Drive not found"
            }),404
        
        drv.status = "Approved"
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"drive approved"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500

@admin_bp.route('/placement-drives/delete-drive',methods=["DELETE"])
@login_required('admin')  
def reject_drive():
    try:
        data = request.get_json() 
        dr_id = data["drive_id"]
       
        drv = CampusDrive.query.filter_by(id = dr_id).first()
        if not drv:
            return jsonify({
                "success":False,
                "message":"Drive not found"
            }),404
        
        db.session.delete(drv)
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"drive rejected"
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something went wrong {e}"
        }),500





@admin_bp.route('/placement-drives',methods=["GET"])
@login_required('admin')  
def manage_placements():
    try:
        pending_drvs = CampusDrive.query.filter_by(status='Pending').all()
        ongoing_drvs = CampusDrive.query.filter(CampusDrive.status=='Approved', CampusDrive.deadline > datetime.now())
        user_name = 'admin'
        on_going = []
        for d in ongoing_drvs:
            apps = len(d.applications)
            apps_pas = Application.query.filter(Application.drive_id == d.id,Application.status == "Shortlisted").count()
            comp = Company.query.filter_by(id=d.company_id).first()
            on_going.append({
                "Title":d.job_title,
                "company":comp.name,
                "package":d.package_lpa,
                "drive_id":d.id,
                "students_applied":apps,
                "students_selected":apps_pas 
            })
            
        pending_ds = []
        for d in pending_drvs:
            comp = Company.query.filter_by(id=d.company_id).first()
            off = officers.query.filter_by(company_id=comp.id,is_recruiter=True).first()
            pending_ds.append({
                "Title":d.job_title,
                "company":comp.name,
                "package":d.package_lpa,
                "Hr_mail":off.email,
                "drive_id":d.id  
            })

        return jsonify({
            "success":True,
            "pending_drive":pending_ds,
            "ongoing_drive":on_going,
            "user_name":user_name
        }),200
    except Exception as e:
        return jsonify({
            "success":False,
            "message":f"Something Went wrong {e}"
        }),500
        







    

        





