 const {createApp} = Vue
    createApp({
        data(){
            return {
                user_name:"",
                pending_drives:[],
                on_going:[],
            }
        },
        created(){
            this.fetchDrives();
        },
        methods:{
            async fetchDrives(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/placement-drives`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error("Failed to fetch placement drives");
                    const data = await res.json();
                    this.user_name = data.user_name;
                    this.pending_drives = data.pending_drive;
                    console.log()
                    this.on_going = data.ongoing_drive;
                }catch(err){
                    console.log(err);
                }
            },
            async handleDriveAction(drive_id, action){
                try{
                    let ac_url;
                    if(action == "Approved"){
                        ac_url = `http://127.0.0.1:5000/admin/placement-drives/accept-drive`
                    }else{
                        ac_url = `http://127.0.0.1:5000/admin/placement-drives/delete-drive`
                    }
                    const formData = new FormData();
                    formData.append("drive_id", drive_id);
                    formData.append("action", action);
                    const res = await fetch(ac_url,{
                        method:"POST",
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData,
                    });
                    console.log(res)
                    if(!res.ok) throw new Error("Failed to update drive status");
                    this.fetchDrives();
                }catch(err){
                    console.log(err);
                }
            }
        }
    }).mount("#app");