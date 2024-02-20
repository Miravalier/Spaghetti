import { apiRequest, session } from "./requests.js";


window.addEventListener("load", async () => {
    await session.load();
    await render();
});


async function render() {
    console.log("[*] Rendering app");

    const pagesDiv = document.body.appendChild(document.createElement("div"));
    pagesDiv.id = "pageLinks";
    pagesDiv.innerHTML = `
        <a href="/account">Account</a>
        <a href="/friends" class="selected">Friends</a>
        <a href="/settings">Settings</a>
    `;
}
