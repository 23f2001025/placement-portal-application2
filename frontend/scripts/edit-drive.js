
const { createApp } = Vue;

createApp({

    data(){

        return {

            drives: [],

            user_name: "",

            message: "",


           
            scheduleDriveId: null,


            
            scheduleForm: {

                interview_date: "",
                start_time: "",
                end_time: "",
                number_of_panels: 1,
                average_time:10,

            }

        }

    },


    created(){

        this.fetchDrives();

    },


    methods: {


        async fetchDrives(){

            try{

                const res = await fetch(
                    `http://127.0.0.1:5000/company/view-drives`,
                    {
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    }
                );

                if(!res.ok)
                    throw new Error("something went wrong");

                const data = await res.json();

                if(!data.success)
                    throw new Error(data.message);

                this.drives = data.drives;

                this.user_name = data.user_name;

            }
            catch(err){

                this.message = err.message;

                console.log(err);

            }

        },


        editDrive(driveId){

            window.location.href =
                `add-drivedetails.html?id=${driveId}`;

        },


        async closeApplications(driveId){

            if(!confirm("Close applications for this drive?"))
                return;

            try{

                const res = await fetch(
                    `http://127.0.0.1:5000/company/edit-drives/${driveId}`,
                    {
                        method:'POST',
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    }
                );

                const data = await res.json();

                if(!data.success)
                    throw new Error(data.message);

                const drive =
                    this.drives.find(d => d.drive_id === driveId);

                if(drive)
                    drive.applications_closed = true;

                this.message =
                    "Applications closed successfully";

                this.fetchDrives();

            }
            catch(err){

                this.message = err.message;

                console.log(err);

            }

        },
         async viewReport(reportUrl){
                try{
                    
                    const res = await fetch(`${reportUrl}`, {
                        headers: {
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch offer letter");

                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    window.open(url, "_blank");

                }catch(err){
                    alert(err.message);
                    console.log(err);
                }
            },


        async openApplications(driveId){

            if(!confirm("Open applications for this drive?"))
                return;

            try{

                const res = await fetch(
                    `http://127.0.0.1:5000/company/edit-drives/open/${driveId}`,
                    {
                        method:'PUT',
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    }
                );

                const data = await res.json();

                if(!data.success)
                    throw new Error(data.message);

                const drive =
                    this.drives.find(d => d.drive_id === driveId);

                if(drive)
                    drive.applications_closed = true;

                this.message =
                    "Applications Opened successfully";

                this.fetchDrives();

            }
            catch(err){

                this.message = err.message;

                console.log(err);

            }

        },


        async deleteDrive(driveId){

            if(!confirm(
                "Are you sure you want to delete this drive? This cannot be undone."
            ))
                return;

            try{

                const res = await fetch(
                    `http://127.0.0.1:5000/company/edit-drives/${driveId}`,
                    {
                        method:'DELETE',
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    }
                );

                const data = await res.json();

                if(!data.success)
                    throw new Error(data.message);

                this.drives =
                    this.drives.filter(
                        d => d.drive_id !== driveId
                    );

                this.message =
                    "Drive deleted successfully";

            }
            catch(err){

                this.message = err.message;

                console.log(err);

            }

        },


     


        showScheduleForm(driveId){

           
            if(this.scheduleDriveId === driveId){

                this.scheduleDriveId = null;

                return;

            }


            this.scheduleDriveId = driveId;


            
            this.scheduleForm = {

                interview_date: "",
                start_time: "",
                end_time: "",
                number_of_panels: 1

            };

        },
        async exportReport(){
            this.generatingReport = true;
            this.reportUrl = "";
            this.message = "";
            try{
                const res = await fetch(`http://127.0.0.1:5000/company/export-report`, {
                    method: "POST",
                    headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                    },
                });
                const data = await res.json();
                if(!res.ok || !data.success) throw new Error(data.message || "Failed to generate report");
                this.reportUrl = `http://127.0.0.1:5000${data.report_url}`;
                this.message = "Your report is ready.";
                this.messageCategory = "success";
            }catch(err){
                this.message = err.message;
                this.messageCategory = "error";
            }finally{
                this.generatingReport = false;
            }
        },


        cancelSchedule(){

            this.scheduleDriveId = null;

            this.scheduleForm = {

                interview_date: "",
                start_time: "",
                end_time: "",
                number_of_panels: 1

            };

        },


        async scheduleInterviews(){

            try{

                
                const driveId = this.scheduleDriveId;


                if(!driveId){

                    throw new Error(
                        "Drive ID is missing"
                    );

                }


               
                const formData = new FormData();

                formData.append(
                    "drive_id",
                    driveId
                );

                formData.append(
                    "interview_date",
                    this.scheduleForm.interview_date
                );

                formData.append(
                    "start_time",
                    this.scheduleForm.start_time
                );

                formData.append(
                    "end_time",
                    this.scheduleForm.end_time
                );

                formData.append(
                    "number_of_panels",
                    this.scheduleForm.number_of_panels
                );
                formData.append(
                    "average_time",
                    this.scheduleForm.average_time
                );



                console.log(
                    "Scheduling:",
                    driveId,
                    this.scheduleForm
                );


                const res = await fetch(
                    `http://127.0.0.1:5000/company/schedule-interviews`,
                    {
                        method: "POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData
                    }
                );


                const data = await res.json();


                if(!res.ok || !data.success){

                    throw new Error(
                        data.message ||
                        "Failed to schedule interviews"
                    );

                }


                this.message =
                    data.message ||
                    "Interviews scheduled successfully";


               
                this.scheduleDriveId = null;


               
                this.scheduleForm = {

                    interview_date: "",
                    start_time: "",
                    end_time: "",
                    number_of_panels: 1

                };
                


            }
            catch(err){

                this.message = err.message;

                console.log(err);

            }

        }

    }

}).mount("#app");