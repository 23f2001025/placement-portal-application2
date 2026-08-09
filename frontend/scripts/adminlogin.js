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
                    const res = await fetch(`http://127.0.0.1:5000/admin/login`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                        },
                        credentials: 'include',
                        body: JSON.stringify({
                            "username":this.username,
                            "password":this.password,
                        })
                    });
                    
                    if(!res.ok) throw new Error('Failed login');
                    const data = await res.json();
                    console.log(data);
                    if(!data.success){
                        this.message= data.message;
                        return;
                    }
                    this.message = "Login Successfull , Redirecting to dashboard!"
                    console.log(data)

                    localStorage.setItem("token", data.token);
                    localStorage.setItem("user_name", data.user_name)

                    window.location.href = 'admindash.html'
                    
                    
                }catch(err){
                    console.log(err);
                    this.message = err;
                }
                
            },
           
        }
    }).mount("#app")