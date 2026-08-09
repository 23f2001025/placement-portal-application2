const {createApp} = Vue;
    createApp({
        data(){
            return {
                company_name:"",
                hr_email:"",
                hr_name:"",
                password1:"",
                password2:"",
                message:"",
            }
        },
        methods:{
            async register(){
                try{
                    if(this.password1 != this.password2){
                        this.message = "Passwords mismatch";
                        return;
                    }
                    console.log(this.company_name+" "+this.password2);
                    
                    const res = await fetch(`http://127.0.0.1:5000/company/register`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'Application/json'
                        },
                        body:JSON.stringify({
                            "company_name":this.company_name,
                            "hr_email":this.hr_email,
                            "hr_name":this.hr_name,
                            "password1":this.password1,
                            "password2":this.password2,
                        })
                    });
                    console.log(res);
                    if(!res.ok) throw new Error("Registration failed");
                    const data = await res.json();
                    if(!data.success) throw new Error("Registratoin failed "+data.message);
                    this.message = data.message;
                    window.location.href = 'companylogin.html';
                }catch(err){
                    this.message = err;
                    console.log(err);

                }
            }
        }
    }).mount("#app");