import { apiRequest, session } from "./requests.js";
import * as header from "./header.js";


window.addEventListener("load", async () => {
    await session.load();
    await render();
});


async function render() {
    console.log("[*] Rendering app");

    await header.render("Settings");

    const settingsContainer = document.createElement("div");
    settingsContainer.id = "settingsContainer";

    const logOutButton = settingsContainer.appendChild(document.createElement("button"));
    logOutButton.innerText = "Log Out";
    logOutButton.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    });

    document.body.appendChild(settingsContainer);
}
