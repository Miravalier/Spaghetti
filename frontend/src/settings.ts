import { apiRequest, session } from "./requests.js";
import { InviteCode } from "./models.js"
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

    const inviteLinkButton = settingsContainer.appendChild(document.createElement("button"));
    inviteLinkButton.className = "field";
    inviteLinkButton.innerText = "Invite a Friend";
    inviteLinkButton.addEventListener("click", async () => {
        const response: {
            status: string;
            code: string;
        } = await apiRequest("POST", "/invite", {});
        window.location.reload();
    });

    const invitesResponse: {
        status: string;
        invites: InviteCode[];
    } = await apiRequest("GET", "/invites");

    if (invitesResponse.invites.length != 0) {
        const invitesField = settingsContainer.appendChild(document.createElement("div"));
        invitesField.className = "invites";

        const invitesTitle = invitesField.appendChild(document.createElement("div"));
        invitesTitle.innerText = "Invite Links";
        invitesTitle.className = "title";

        for (const invite of invitesResponse.invites) {
            const inviteContainer = invitesField.appendChild(document.createElement("div"));
            inviteContainer.className = "invite";

            const urlItem = inviteContainer.appendChild(document.createElement("a"));
            urlItem.className = "item";
            urlItem.innerText = `${window.location.origin}/register?code=${invite.code}`;

            const dateItem = inviteContainer.appendChild(document.createElement("div"));
            dateItem.className = "item";
            dateItem.innerText = "Created: " + invite.date.split("T")[0];

            const cancelButton = inviteContainer.appendChild(document.createElement("button"));
            cancelButton.className = "item";
            cancelButton.innerText = "X";
            cancelButton.addEventListener("click", async () => {
                await apiRequest("DELETE", "/invite", { code: invite.code });
                window.location.reload();
            });
        }
    }

    const verifyResponse: {
        status: string;
        token: string;
    } = await apiRequest("GET", "/verification");

    const verificationContainer = settingsContainer.appendChild(document.createElement("div"));
    verificationContainer.className = "field column";
    verificationContainer.innerHTML = `
        <div class="label">Verification Token</div>
        <div class="token">${verifyResponse.token}</div>
        <p>Do not share this token with anyone except spaghetti@miramontes.dev</p>
    `;

    document.body.appendChild(settingsContainer);
}
