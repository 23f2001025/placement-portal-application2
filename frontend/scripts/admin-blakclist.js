const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                blacklistedCompanies:[],
                blacklistedStudents:[],
                loading:true,
                message:"",
                successMessage:"",
                removingId:null,
            }
        },
        created(){
            this.fetchBlacklist();
        },
        methods:{
            async fetchBlacklist(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/blacklist`, {
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch blacklist");
                    const data = await res.json();
                    if(!data.success) throw new Error(data.message || "Failed to fetch blacklist");

                    this.user_name = data.user_name;
                    this.blacklistedCompanies = data.companies || [];
                    this.blacklistedStudents = data.students || [];
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                }finally{
                    this.loading = false;
                }
            },

            async removeFromBlacklist(type, id){
                if(!confirm("Remove this " + type + " from the blacklist?")) return;

                this.removingId = id;
                this.message = "";
                this.successMessage = "";

                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/blacklist/${type}/${id}`, {
                        method:"DELETE",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    const data = await res.json();
                    if(!res.ok || !data.success) throw new Error(data.message || "Failed to remove from blacklist");

                    if(type === "company"){
                        this.blacklistedCompanies = this.blacklistedCompanies.filter(c => c.company_id !== id);
                    }else{
                        this.blacklistedStudents = this.blacklistedStudents.filter(s => s.student_id !== id);
                    }

                    this.successMessage = "Removed from blacklist successfully";
                    this.fetchBlacklist();
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                }finally{
                    this.removingId = null;
                }
            }
        }
    }).mount("#app");