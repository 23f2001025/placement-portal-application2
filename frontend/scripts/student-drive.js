 const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                drives:[],
                message:"",
                messageCategory:"",
            }
        },
        created(){
            this.fetchDrives();
        },
        methods:{
            async fetchDrives(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/student/apply`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch placement drives");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.drives = data.drives;
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            },
            async submitApplication(event, drive_id){
                try{
                    const formData = new FormData(event.target);
                    const res = await fetch(`http://127.0.0.1:5000/student/apply`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to submit application");
                    this.message = data.message;
                    this.messageCategory = "success";
                    this.fetchDrives();
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            }
        }
    }).mount("#app");