const {createApp} = Vue;
    createApp({
        data(){
            return {
                user_name:"",
                message:"",
                announcements:[],
                drives:[],
                applications:[],
            }
        },
        created(){
            this.fetchDashDetails();
        },
        methods:{
            async fetchDashDetails(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/student/dashboard`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Exception("Error loadinf dashboard");
                    const data = await res.json();
                    if(!data.success) throw new Error(data.message);
                    this.user_name = data.user_name;
                    this.applications = data.applications;
                    this.drives = data.drives;
                    this.announcements = data.announcements;
                    return;
                }catch(err){
                    this.message = err;
                    console.log(err);
                }
            },
            formatDate(dateStr){
                const d = new Date(dateStr);
                return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
            }
        }
    }).mount("#app");