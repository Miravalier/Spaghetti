import { apiRequest } from "./requests.js";
import { session } from "./session.js";

window.addEventListener("load", async () => {
    // Try to grab the token from storage
    session.token = localStorage.getItem("token");
    if (session.token == null) {
        window.location.href = "/login";
    }

    // Try to make a status request with this token
    try {
        await apiRequest("GET", "/status");
    } catch (error) {
        window.location.href = "/login";
    }
});
