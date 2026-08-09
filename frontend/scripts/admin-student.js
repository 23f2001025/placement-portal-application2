const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                announcements:[],
                headline:"",
                announceText:"",
                search_id:"",
                search_by:"name",
                searched:false,
                search_results:[],
                student_reg:[],
                student_placed:[],
            }
        },
        created(){
            this.fetchStudentsData();
        },
        methods:{
            async fetchStudentsData(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/managestudents`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                    });
                    if(!res.ok) throw new Error("Failed to fetch students data");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.announcements = data.announcements;
                    this.student_reg = data.registered_students;
                    this.student_placed = data.placed_students;
                }catch(err){
                    console.log(err);
                }
            },
            async submitAnnouncement(){
                try{
                    const formData = new FormData();
                    console.log(this.headline)
                    console.log(this.announceText)
                    formData.append("action", "announce");
                    formData.append("headline", this.headline);
                    formData.append("text", this.announceText);
                    const res = await fetch(`http://127.0.0.1:5000/admin/managestudents/announcement`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    if(!res.ok) throw new Error("Failed to submit announcement");
                    this.headline = "";
                    this.announceText = "";
                    this.fetchStudentsData();
                }catch(err){
                    console.log(err);
                }
            },
            async deleteAnnouncement(announce_id){
                try{
                    
                    
                    const res = await fetch(`http://127.0.0.1:5000/admin/managestudents/delete-announcement/${announce_id}`,{
                        method:"DELETE",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                    
                    });
                    if(!res.ok) throw new Error("Failed to delete announcement");
                    this.fetchStudentsData();
                }catch(err){
                    console.log(err);
                }
            },
            async submitSearch(){
                try{
                    const formData = new FormData();
                    formData.append("action", "search");
                    formData.append("search_id", this.search_id);
                    formData.append("search_by", this.search_by);
                    const res = await fetch(`http://127.0.0.1:5000/admin/managestudents/search-student`,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    if(!res.ok) throw new Error("Failed to search students");
                    const data = await res.json();
                    this.search_results = data.search_result || [];
                    this.searched = true;
                }catch(err){
                    console.log(err);
                }
            },
            async handleStudentAction(student_id, action){
                try{
                    const formData = new FormData();
                    let ac_url = `http://127.0.0.1:5000/admin/managestudents/search-student`
                    if(action == "blacklist"){
                        ac_url = `http://127.0.0.1:5000/admin/managestudents/blacklist`
                    }else{
                        ac_url = `http://127.0.0.1:5000/admin/managestudents/remove`
                    }
                    formData.append("student_id", student_id);
                    formData.append("action", action);
                    console.log(ac_url)
                    const res = await fetch(ac_url,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    if(!res.ok) throw new Error("Failed to update student");
                    this.fetchStudentsData();
                }catch(err){
                    console.log(err);
                }
            }
        }
    }).mount("#app");