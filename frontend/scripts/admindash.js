const {createApp} = Vue 
    createApp({
        data(){
            return {
                user_name:"",
                student_count:null,
                company_count:null,
                going_drives:[],
                upcoming_drives:[],
                searchQuery: '',
                searchResults:[],
            }
        },
        created(){
            this.fetchDashData();
        },
        methods:{
            async fetchDashData(){
                try{
                    console.log("hello")
                    console.log(localStorage.getItem("token"));
                    const res = await fetch(`http://127.0.0.1:5000/admin/dashboard`, {
            headers:{
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
                    console.log(res);
                    if(!res.ok) throw new Error('Failed to fetch dashboard data');
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.student_count = data.student_count;
                    this.company_count = data.company_count;
                    this.going_drives =data.ongoing_drives;
                    this.upcoming_drives = data.upcoming_drives;
                    

                }catch(err){
                    console.log(err);
                }
            },
            async searchStudents(){
                try{
                    const res = await fetch(`api/?q=${encodeURIComponent(this.searchQuery)}`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    const data = await res.json();
                    this.searchResults = data.results || [];
                }catch(err){
                    console.log(err);
                }
                
            }
        }
    }).mount("#app");