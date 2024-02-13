import { apiRequest } from "./requests.js";


window.addEventListener("load", async () => {
    // Try to grab the token from storage
    let token = localStorage.getItem("token");
    if (token != null) {
        // Try to make a status request with this token
        try {
            await apiRequest("GET", "/status");
            window.location.href = "/";
            return;
        }
        catch (error) { }
    }

    document.getElementById("login-button").addEventListener('click', async () => {
        const usernameElement = document.getElementById("username") as HTMLInputElement;
        const passwordElement = document.getElementById("password") as HTMLInputElement;
        const response = await apiRequest(
            "POST", "/login",
            { username: usernameElement.value, password: passwordElement.value }
        );
        if (response.status == "success") {
            localStorage.setItem("token", response.token);
            window.location.href = "/";
        }
    });
});
