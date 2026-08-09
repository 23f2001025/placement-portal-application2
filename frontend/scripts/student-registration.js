const {createApp} = Vue;
    createApp({
        data(){
            return {
                enroll_no:"",
                mail_id:"",
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
                    
                    
                    const res = await fetch(`http://127.0.0.1:5000/student/register`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'Application/json'
                        },
                        body:JSON.stringify({
                            "enroll_no":this.enroll_no,
                            "mail_id":this.mail_id,
                            "password1":this.password1,
                            "password2":this.password2,
                        })
                    });
                   
                    if(!res.ok) throw new Error("Registration failed");
                    const data = await res.json();
                    if(!data.success) throw new Error("Registratoin failed "+data.message);
                    this.message = data.message;
                    window.location.href = 'studentlogin.html';
                }catch(err){
                    this.message = err;
                    console.log(err);

                }
            }
        }
    }).mount("#app");