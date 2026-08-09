const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                applications:[],
                shortlisted:[],
                interviewScheduled:[],
                selected:[],
                message:"",
                messageCategory:"",
                offerModalAppId: null,
                offerFile: null,
                uploadingOffer: false,
                offerModalInstance: null,
            }
        },
        created(){
            this.fetchApplications();
        },
        mounted(){
            this.offerModalInstance = new bootstrap.Modal(document.getElementById("offerModal"));
        },
        methods:{
            async fetchApplications(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/company/applications`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                    });
                    if(!res.ok) throw new Error("Failed to fetch applications");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.applications = data.applications;
                    this.shortlisted = data.shortlisted;
                    this.interviewScheduled = data.interview || [];
                    this.selected = data.selected || [];
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            },
            async handleApplicationAction(application_id, action){
                try{
                    const formData = new FormData();
                    formData.append("application_id", application_id);
                    formData.append("action", action);
                    console.log(application_id,action);
                    const res = await fetch(`http://127.0.0.1:5000/company/applications`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to update application");
                    this.message = data.message;
                    this.messageCategory = "success";
                    this.fetchApplications();
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            },
            openOfferModal(appId){
                this.offerModalAppId = appId;
                this.offerFile = null;
                this.offerModalInstance.show();
            },
            onOfferFileSelected(e){
                this.offerFile = e.target.files[0];
            },
            async uploadOfferLetter(){
                if(!this.offerFile){
                    alert("Please select a PDF file first");
                    return;
                }
                this.uploadingOffer = true;
                try{
                    const formData = new FormData();
                    formData.append("offer_letter", this.offerFile);

                    const res = await fetch(`http://127.0.0.1:5000/company/applications/${this.offerModalAppId}/upload-offer`, {
                        method: "POST",
                        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` },
                        body: formData
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Upload failed");

                    this.offerModalInstance.hide();
                    this.fetchApplications(); 
                }catch(err){
                    alert(err.message);
                }finally{
                    this.uploadingOffer = false;
                }
            },
            async viewResume(appId){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/company/student-resume/${appId}`, {
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
            }
        }
    }).mount("#app");