import { apiRequest } from "./requests.js";
import { session } from "./session.js";

window.addEventListener("load", () => {
    // Try to grab the token from storage
    session.token = localStorage.getItem("token");
    if (session.token != null) {
        // Try to make a status request with this token
        apiRequest("GET", "/status");
        window.location.href = "/";
        return;
    }

    document.getElementById("login-button").addEventListener('click', async () => {
        const usernameElement = document.getElementById("username") as HTMLInputElement;
        const passwordElement = document.getElementById("password") as HTMLInputElement;
        const response = await apiRequest(
            "POST", "/login",
            { username: usernameElement.value, password: passwordElement.value }
        );
        if (response.status == "success") {
            session.token = response.token;
            localStorage.setItem("token", response.token);
            window.location.href = "/";
        }
    });
});
