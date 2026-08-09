const {createApp} = Vue
    createApp({
        data(){
            return {
                drive_id: null,
                user_name:"",
                message:"",
                successMessage:"",
                loading:true,
                saving:false,

                
                drive: {
                    job_title:"",
                    package_lpa:"",
                    cutoff_cgpa:"",
                    location:"",
                    allowed_branches:"",
                    deadline:"",
                    drive_date:"",
                    job_description:"",
                    rounds_description:"",
                },

                // field definitions used to render rows + the modal
                fields: [
                    { key:"job_title", label:"Title" },
                    { key:"package_lpa", label:"Package" },
                    { key:"cutoff_cgpa", label:"CGPA Required" },
                    { key:"location", label:"Location" },
                    { key:"allowed_branches", label:"Allowed Branches" },
                    { key:"deadline", label:"Deadline" },
                    { key:"drive_date", label:"Start Date" },
                    { key:"job_description", label:"Description", multiline:true },
                    { key:"rounds_description", label:"Rounds", multiline:true },
                ],

                
                editedFields: new Set(),

                
                editingField: null,
                editingValue: "",
                modalInstance: null,
            }
        },
        created(){
            const params = new URLSearchParams(window.location.search);
            this.drive_id = params.get("id");
            if(!this.drive_id){
                this.message = "No drive id provided";
                this.loading = false;
                return;
            }
            this.fetchDriveDetails();
        },
        mounted(){
            this.modalInstance = new bootstrap.Modal(document.getElementById("editFieldModal"));
        },
        methods:{
            async fetchDriveDetails(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/company/drive?id=${this.drive_id}`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch drive details");
                    const data = await res.json();
                    if(!data.success) throw new Error(data.message || "Failed to fetch drive details");

                    this.user_name = data.user_name;

                    const d = data.drive;
                    this.drive.job_title = d.job_title;
                    this.drive.package_lpa = d.package_lpa;
                    this.drive.cutoff_cgpa = d.cutoff_cgpa;
                    this.drive.location = d.location;
                    this.drive.allowed_branches = d.allowed_branches;
                    this.drive.deadline = d.deadline;
                    this.drive.drive_date = d.drive_date;
                    this.drive.job_description = d.job_description;
                    this.drive.rounds_description = d.rounds_description;
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                }finally{
                    this.loading = false;
                }
            },

            openEdit(field){
                this.editingField = field;
                this.editingValue = this.drive[field.key];
                this.modalInstance.show();
            },

            saveFieldEdit(){
                if(!this.editingField) return;
                this.drive[this.editingField.key] = this.editingValue;
                this.editedFields.add(this.editingField.key);
                this.modalInstance.hide();
                this.editingField = null;
                this.editingValue = "";
            },

            async updateDrive(){
                if(this.editedFields.size === 0) return;

                this.saving = true;
                this.message = "";
                this.successMessage = "";

                
                const payload = {};
                this.editedFields.forEach(key => {
                    payload[key] = this.drive[key];
                });

                try{
                    const res = await fetch(`http://127.0.0.1:5000/company/edit-drives/${this.drive_id}`,{
                        method:"PUT",
                        credentials:"include",
                        headers: { "Content-Type": "application/json" , "Authorization": `Bearer ${localStorage.getItem("token")}`},
                        body: JSON.stringify(payload),
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to update drive");

                    this.successMessage = "Drive updated successfully";
                    this.editedFields.clear();
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                }finally{
                    this.saving = false;
                }
            }
        }
    }).mount("#app");