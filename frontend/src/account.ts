import { apiRequest, session } from "./requests.js";
import { Lock } from "./utils.js";
import { User } from "./models.js";


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
        <a href="/account" class="selected">Account</a>
        <a href="/friends">Friends</a>
        <a href="/settings">Settings</a>
    `;

    const balanceDiv = document.body.appendChild(document.createElement("div"));
    balanceDiv.id = "balanceSection";
    balanceDiv.innerHTML = `
        <div class="balance">Spaghetti: 42</div>
        <div class="buttons">
            <button type="button" id="send">Send</button>
            <button type="button" id="request">Request</button>
        </div>
    `;

    const transactionLog = document.body.appendChild(document.createElement("div"));
    transactionLog.id = "transactionLog";

    loadBalance();
}


async function loadBalance() {
    const response: {
        status: string;
        user: User;
    } = await apiRequest("GET", "/status");

    const balance = document.querySelector("#balanceSection .balance") as HTMLDivElement;
    balance.innerText = `Spaghetti: ${response.user.balance.toFixed(2)}`;
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
