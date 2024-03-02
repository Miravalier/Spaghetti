import { apiRequest } from "./requests.js";
import { renderErrorMessage } from "./dialog.js";


window.addEventListener("load", async () => {
    const searchParams = new URLSearchParams(window.location.search);
    const invite_code = searchParams.get("code");
    if (!invite_code) {
        await renderErrorMessage("Missing invite code!");
        window.location.href = "/login";
    }

    const usernameElement = document.getElementById("username") as HTMLInputElement;
    const passwordElement = document.getElementById("password") as HTMLInputElement;
    const confirmElement = document.getElementById("confirmPassword") as HTMLInputElement;

    document.getElementById("register-button").addEventListener('click', async () => {
        if (!usernameElement.value || !passwordElement.value) {
            renderErrorMessage("Username and password cannot be empty.");
            return;
        }

        if (passwordElement.value != confirmElement.value) {
            renderErrorMessage("Passwords do not match.");
            return;
        }

        try {
            const response = await apiRequest(
                "POST", "/register",
                {
                    username: usernameElement.value,
                    password: passwordElement.value,
                    invite_code,
                }
            );
            if (response.status == "success") {
                localStorage.setItem("token", response.token);
                window.location.href = "/";
            }
        } catch (error) {
            renderErrorMessage(error);
            return;
        }
    });
});
