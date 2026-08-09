 const {createApp} = Vue;
    createApp({
        data(){
            return {
                student_applications:[],
                drives:[],
                user_name:"",
                message:"",
            }
        },
        created(){
            this.fetchCompanyData();
        },
        methods:{
            async fetchCompanyData(){
                try{

                    console.log("hello")
                    const res = await fetch(`http://127.0.0.1:5000/company/dashboard`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    console.log(res)
                    if(!res.ok) throw new Exception("something went wrong ");
                    const data = await res.json();
                    console.log(data)
                    if(!data.success) throw new Exception(data.message);
                    this.student_applications = data.student_applications;
                    this.drives = data.drives;
                    this.user_name = data.user_name;
                    return;
                }catch(err){
                    this.message =err;
                    console.log(err);
                }
            }
        }
    }).mount("#app");