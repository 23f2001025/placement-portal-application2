const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                student:{},
                emailInput:"",
                message:"",
                messageCategory:"",
            }
        },
        created(){
            this.fetchProfile();
        },
        methods:{
            async fetchProfile(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/student/profile`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch profile");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.student = data.student;
                    this.emailInput = data.student.email || "";
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            },
            async updateEmail(){
                try{
                    const formData = new FormData();
                    formData.append("email", this.emailInput);
                    const res = await fetch(`http://127.0.0.1:5000/student/profile`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to update email");
                    this.message = data.message;
                    this.messageCategory = "success";
                    this.fetchProfile();
                }catch(err){
                    this.message = err.message;
                    this.messageCategory = "error";
                    console.log(err);
                }
            }
        }
    }).mount("#app");