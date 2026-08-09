const {createApp} = Vue;
    createApp({
        data(){
            return {
                username:"",
                password:"",
                message:"",
            }
        },
        methods:{
            async login(){
                try{
                    console.log(this.username)
                    const res = await fetch(`http://127.0.0.1:5000/student/login`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                        },
                        credentials: 'include',
                        body: JSON.stringify({
                            "enroll_no":this.username,
                            "password":this.password,
                        })
                    });
                    
                    if(!res.ok) throw new Error('Failed to create drive');
                    const data = await res.json();
                    console.log(data);
                    if(!data.success){
                        this.message= data.message;
                        return;
                    }
                    console.log(data);
                    this.message = "Login Successfull , Redirecting to dashboard!"
                    localStorage.setItem("token", data.token);
                    localStorage.setItem("user_name", data.user_name);
                    window.location.href = 'student-dash.html'
                }catch(err){
                    console.log(err);
                    this.message = err;
                }
                
            } 
        }
    }).mount("#app")