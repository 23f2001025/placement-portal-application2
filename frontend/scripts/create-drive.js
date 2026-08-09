const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                drives:[],
                message:"",
                job_title:"",
                package:"",
                cutoff_cgpa:"",
                location:"",
                branches:"",
                deadline:"",
                drive_date:"",
                description:"",
                Round_Description:"",
            }
        },
        created(){
            this.fetchCreateDriveData();
        },
        methods:{
            async fetchCreateDriveData(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/company/create-drive`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                    });
                    if(!res.ok) throw new Error("Failed to fetch data");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.drives = data.drives;
                }catch(err){
                    console.log(err);
                }
            },
            async createDrive(){
                try{
                    const formData = new FormData();
                    formData.append("job_title", this.job_title);
                    formData.append("package", this.package);
                    formData.append("cutoff-cgpa", this.cutoff_cgpa);
                    formData.append("location", this.location);
                    formData.append("branches", this.branches);
                    formData.append("deadline", this.deadline);
                    formData.append("drive-date", this.drive_date);
                    formData.append("description", this.description);
                    formData.append("Round-Description", this.Round_Description);
                    const res = await fetch(`http://127.0.0.1:5000/company/create-drive`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to create drive");
                    this.message = "";
                    this.job_title = "";
                    this.package = "";
                    this.cutoff_cgpa = "";
                    this.location = "";
                    this.branches = "";
                    this.deadline = "";
                    this.drive_date = "";
                    this.description = "";
                    this.Round_Description = "";
                    this.fetchCreateDriveData();
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                }
            }
        }
    }).mount("#app");