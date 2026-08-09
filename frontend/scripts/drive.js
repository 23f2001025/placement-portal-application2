const {createApp} = Vue
    createApp({
        data(){
            return {
                drive:{},
            }
        },
        created(){
            this.fetchDriveDetails();
        },
        methods:{
            async fetchDriveDetails(){
                try{
                    const params = new URLSearchParams(window.location.search);
                    const id = params.get("id");
                    const res = await fetch(`http://127.0.0.1:5000/company/drive?id=${id}`);
                    if(!res.ok) throw new Error("Failed to fetch drive details");
                    const data = await res.json();
                    this.drive = data.drive;
                }catch(err){
                    console.log(err);
                }
            }
        }
    }).mount("#app");