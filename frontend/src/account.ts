import { apiRequest, session, getUserByName } from "./requests.js";
import { User, Transaction } from "./models.js";
import { ButtonDialog } from "./dialog.js";


window.addEventListener("load", async () => {
    await session.load();
    await render();
});


async function render() {
    console.log("[*] Rendering app");

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
        <div class="balance"></div>
        <div class="buttons">
            <button type="button" id="send">Send</button>
            <!-- <button type="button" id="request">Request</button> -->
        </div>
    `;

    const sendButton = balanceDiv.querySelector<HTMLButtonElement>("#send");
    sendButton.addEventListener("click", async () => {
        const dialogResults = await new ButtonDialog(`
            <div class="field">
                <div class="label">User</div>
                <input name="username"></input>
            </div>
            <div class="field">
                <div class="label">Amount</div>
                <input name="amount" type="number" step="0.01" min="0"></input>
            </div>
        `, ["Send", "Cancel"]).render();

        if (dialogResults.button != "Send") {
            return;
        }

        console.log("Button Pressed:", dialogResults);
        const destination = await getUserByName(dialogResults.data.username);
        console.log(destination, dialogResults.data.amount);
    });

    const transactionLog = document.body.appendChild(document.createElement("div"));
    transactionLog.id = "transactionLog";

    loadBalance();
    loadTransactions();
}


async function loadBalance() {
    const response: {
        status: string;
        user: User;
    } = await apiRequest("GET", "/status");

    const balanceElement = document.querySelector("#balanceSection .balance") as HTMLDivElement;
    balanceElement.innerText = `Spaghetti: ${Number(response.user.balance).toFixed(2)}`;
}


async function loadTransactions() {
    const response: {
        status: string;
        transactions: Transaction[];
    } = await apiRequest("GET", "/transactions");

    const transactionLogElement = document.querySelector("#transactionLog") as HTMLDivElement;
    const headerElement = transactionLogElement.appendChild(document.createElement("div"));
    headerElement.className = "header row";
    headerElement.innerHTML = `
        <div class="account field">Account</div>
        <div class="comment field">Comment</div>
        <div class="amount field">Amount</div>
        <div class="date field">Date</div>
    `;
    let highlight = true;
    for (const transaction of response.transactions) {
        let accountName: string;
        let amount: string;
        let direction: string;

        // Outbound
        if (transaction.source == session.id) {
            accountName = await getAccountName(transaction.destination);
            amount = "-" + Number(transaction.amount).toFixed(2);
            direction = "outbound";
        }
        // Inbound
        else {
            accountName = await getAccountName(transaction.source);
            amount = "+" + Number(transaction.amount).toFixed(2);
            direction = "inbound";
        }

        const transactionElement = transactionLogElement.appendChild(document.createElement("div"));
        if (highlight) {
            transactionElement.className = "transaction row highlight";
        }
        else {
            transactionElement.className = "transaction row";
        }
        transactionElement.dataset.id = transaction.id;
        transactionElement.innerHTML = `
            <div class="account field">${accountName}</div>
            <div class="comment field">${transaction.comment}</div>
            <div class="amount field ${direction}">${amount}</div>
            <div class="date field">${transaction.date.split("T")[0]}</div>
        `;
        highlight = !highlight;
    }
}


const accountNameCache: { [id: string]: string } = {};


async function getAccountName(id: string): Promise<string> {
    if (id == "system") {
        return "System";
    }
    if (accountNameCache[id] !== undefined) {
        return accountNameCache[id];
    }
    const response: {
        status: string;
        user: User;
    } = await apiRequest("GET", "/user", { id });
    accountNameCache[id] = response.user.name;
    return response.user.name;
}
