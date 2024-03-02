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

    document.body.appendChild(settingsContainer);
}
