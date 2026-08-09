 const {createApp} = Vue;
    createApp({
        data(){
            return {
                company_name:"",
                password:"",
                message:"",
            }
        },
        methods:{
            async login(){
                try{
                    
                    
                    const res = await fetch(`http://127.0.0.1:5000/company/login`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'Application/json'
                        },
                        credentials:'include',
                        body:JSON.stringify({
                            "company_name":this.company_name,
                            "password":this.password,
                           
                        })
                    });
                   
                    if(!res.ok) throw new Error("Login failed");
                    const data = await res.json();
                    if(!data.success) throw new Error("Login failed "+data.message);
                    this.message = data.message;
                    localStorage.setItem("token", data.token);
                    localStorage.setItem("user_name", data.user_name);
                    window.location.href = 'company-dash.html';
                }catch(err){
                    this.message = err.message;
                    console.log(err);
                    return;
                }
            }
        }
    }).mount("#app");