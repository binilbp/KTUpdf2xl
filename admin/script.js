document.getElementById("loginBtn").addEventListener("click", login);

async function login(){

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const error = document.getElementById("error");

    error.innerText = "";

    try{

        const res = await fetch("/auth/admin/login",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
            credentials: "include"
        });

        if(res.ok){
            window.location.href="/static/dashboard.html";
        }
        else{
            error.innerText = "Invalid login";
        }

    }
    catch(err){
        error.innerText = "Server error";
    }

}