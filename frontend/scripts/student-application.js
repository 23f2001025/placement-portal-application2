const {createApp} = Vue;
    createApp({
        data(){
            return {
                student_name:"",
                applications:[],
                message:"",
                interviews:[],

            }
        },
        created(){
            this.fetchData();
        },
        methods:{
            async fetchData(){
                try{
                    
                    
                    
                    const res = await fetch(`http://127.0.0.1:5000/student/view-applications`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                        
                    });
                   
                    if(!res.ok) throw new Error("something went  wrong");
                    const data = await res.json();
                    if(!data.success) throw new Error(" Error  "+data.message);
                    this.applications = data.applications
                    this.student_name=data.student_name
                    this.interviews = data.interviews
                    console.log(JSON.stringify(this.interviews, null, 2))

                }catch(err){
                    this.message = err;
                    console.log(err);

                }
            },
            async viewOfferLetter(appId){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/student/offer-letter/${appId}`, {
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
            },
            async viewResume(driveId){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/student/resume/${driveId}`, {
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