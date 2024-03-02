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

    const logOutField = settingsContainer.appendChild(document.createElement("div"));
    logOutField.className = "field";
    const logOutButton = logOutField.appendChild(document.createElement("button"));
    logOutButton.innerText = "Log Out";
    logOutButton.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    });

    const privacyField = settingsContainer.appendChild(document.createElement("div"));
    privacyField.className = "field";
    privacyField.innerHTML = `
        <div class="label">Privacy</div>
        <select>
            <option value="public">Public</option>
            <option value="friends">Friends Only</option>
            <option value="private">Self Only</option>
        </select>
    `;
    const privacySelect = privacyField.querySelector<HTMLSelectElement>("select");
    privacySelect.value = session.user.privacy;
    privacySelect.addEventListener("change", async () => {
        await apiRequest("PUT", "/user/settings", { privacy: privacySelect.value });
    });

    const response: {
        status: string;
        token: string;
    } = await apiRequest("GET", "/verification");

    const verificationContainer = settingsContainer.appendChild(document.createElement("div"));
    verificationContainer.className = "field column";
    verificationContainer.innerHTML = `
        <div class="label">Verification Token</div>
        <div class="token">${response.token}</div>
        <p>Do not share this token with anyone except spaghetti@miramontes.dev</p>
    `;

    document.body.appendChild(settingsContainer);
}
