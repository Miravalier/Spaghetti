import { apiRequest } from "./requests.js";
import { renderErrorMessage } from "./dialog.js";


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

    const usernameInput = document.getElementById("username") as HTMLInputElement;
    const passwordInput = document.getElementById("password") as HTMLInputElement;
    const loginButton = document.getElementById("login-button") as HTMLButtonElement;

    async function attemptLogin() {
        if (!usernameInput.value || !passwordInput.value) {
            renderErrorMessage("Username and password cannot be empty.");
            return;
        }
        try {
            const response = await apiRequest(
                "POST", "/login",
                { username: usernameInput.value, password: passwordInput.value }
            );
            if (response.status == "success") {
                localStorage.setItem("token", response.token);
                window.location.href = "/";
            }
        } catch (error) {
            renderErrorMessage(error);
            return;
        }

    }

    function onKeypress(ev: KeyboardEvent) {
        if (ev.key == "Enter") {
            ev.preventDefault();
            ev.stopPropagation();
            attemptLogin();
        }
    }

    usernameInput.addEventListener("keypress", onKeypress);
    passwordInput.addEventListener("keypress", onKeypress);
    loginButton.addEventListener('click', attemptLogin);
});
