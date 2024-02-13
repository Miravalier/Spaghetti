import { apiRequest, session } from "./requests.js";
import { Lock } from "./utils.js";


const renderLock = new Lock();


window.addEventListener("load", async () => {
    await session.load();
    await initialRender();
    await renderLock.acquireAndRun(renderUpdate);
    window.addEventListener("resize", () => { renderLock.acquireAndRun(renderUpdate); });
});


async function initialRender() {
    console.log("[*] Rendering app; initial render");

    const pagesDiv = document.body.appendChild(document.createElement("div"));
    pagesDiv.id = "pageLinks";
    pagesDiv.innerHTML = `
        <a href="/account">Account</a>
        <a href="/friends" class="selected">Friends</a>
        <a href="/settings">Settings</a>
    `;
}


async function renderUpdate() {
    console.log("[*] Rendering app; update");

    // Figure out if we're in landscape or portrait
    console.log("[*] Width:", window.innerWidth);
    console.log("[*] Height:", window.innerHeight);
    if (window.innerWidth > window.innerHeight) {
        console.log("[*] Landscape Mode");
    }
    else {
        console.log("[*] Portrait Mode");
    }
}
