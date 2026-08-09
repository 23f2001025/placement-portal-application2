const {createApp} = Vue;
    createApp({
        data(){
            return {
                user_name:"",
                search_id:"",
                search_results:[],
                searchResult:false,
                pending_comps:[],
                approved_comps:[],
               
            }
        },
        created(){
            this.fetchDetails();
        },
        methods:{
            async fetchDetails(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/managecompany`,{
                        headers:{
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    if(!res.ok) throw new Error('Failed to fetch dashboard data');
                    const data = await  res.json();
                    this.user_name= data.user_name;
                    this.pending_comps = data.pending_companies;
                    console.log(this.pending_comps)
                    this.approved_comps = data.approved_companies;
                    return;
                }catch(err){
                    console.log(err);
                }
                
            },
            async search(){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/managecompany/searchCompany`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        credentials:'include',
                        body:JSON.stringify({
                            "search_id":this.search_id
                        })
                    });
                    if(!res.ok) throw new Error('Failed to fetch dashboard data');
                    const data = await  res.json();
                    if(!data.success) throw new Error('Failed to fetch companies');
                    this.searchResult = true;
                    this.search_results = data.search_result;

                    return;
                }catch(err){
                    console.log(err);
                }
                
            },
            async ApproveCompany(company_id){
                console.log(company_id)
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/managecompany/approveCompany`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        credentials:'include',
                        body:JSON.stringify({
                            "company_id":company_id
                        })
                    });
                    if(!res.ok) throw new Error('Failed to approve');
                    const data = await  res.json();
                    if(!data.success) throw new Error('Failed operation!');
                    this.fetchDetails();
                    return;
                }catch(err){
                    console.log(err);
                }
            },
            async blacklistCompany(company_id){
                try{
                    const res = await fetch(`http://127.0.0.1:5000/admin/managecompany/blacklist`,{
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json',
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        credentials:'include',
                        body:JSON.stringify({
                            "company_id":company_id
                        })
                    });
                    if(!res.ok) throw new Error('Failed to approve');
                    const data = await  res.json();
                    if(!data.success) throw new Error('Failed operation!');
                    this.fetchDetails();
                    return;
                }catch(err){
                    console.log(err);
                }
            }
        }
    }).mount("#app");
