import {
    apiRequest,
    getFriendships,
    session,
} from "./requests.js";
import { User, Transaction } from "./models.js";
import { ButtonDialog, renderErrorMessage } from "./dialog.js";
import * as header from "./header.js";


window.addEventListener("load", async () => {
    await session.load();
    await render();
});


async function render() {
    console.log("[*] Rendering app");
    const searchParams = new URLSearchParams(window.location.search);
    const userId = searchParams.get("id");

    await header.render("Account");

    const balanceDiv = document.body.appendChild(document.createElement("div"));
    balanceDiv.id = "balanceSection";
    balanceDiv.innerHTML = `
        <div class="balance"></div>
    `;

    const buttonsDiv = balanceDiv.appendChild(document.createElement("div"));
    buttonsDiv.className = "buttons";

    if (!userId || userId == session.id) {
        const sendButton = buttonsDiv.appendChild(document.createElement("button"));
        sendButton.id = "send";
        sendButton.type = "button";
        sendButton.innerText = "Send";
        sendButton.addEventListener("click", async () => {
            const friendshipOptions: string[] = [];
            for (const { type, id, name } of await getFriendships()) {
                if (type != "completed") {
                    continue;
                }
                friendshipOptions.push(`
                <option value="${id}">${name}</option>
            `);
            }

            if (friendshipOptions.length == 0) {
                await renderErrorMessage("You can only send spaghetti to friends, add a friend first.");
                return;
            }

            const dialogResults = await new ButtonDialog(`
                <div class="field">
                    <div class="label">User</div>
                    <select name="user">
                        ${friendshipOptions}
                    </select>
                </div>
                <div class="field">
                    <div class="label">Amount</div>
                    <input name="amount" type="number" step="0.01" min="0"></input>
                </div>
                <div class="field">
                    <div class="label">Comment</div>
                    <input name="comment" type="text"></input>
                </div>
            `, ["Send", "Cancel"]).render();

            if (dialogResults.button != "Send") {
                return;
            }

            try {
                await apiRequest("POST", "/transfer", {
                    source: session.id,
                    destination: dialogResults.data.user,
                    amount: dialogResults.data.amount,
                    comment: dialogResults.data.comment,
                });
                window.location.reload();
            } catch (error) {
                await renderErrorMessage(error.toString());
            }
        });
    }

    const transactionLog = document.body.appendChild(document.createElement("div"));
    transactionLog.id = "transactionLog";

    await loadBalance(userId);
    await loadTransactions(userId);
}


async function loadBalance(id: string) {
    const data = {};
    if (id) {
        data["id"] = id;
    }
    const balanceElement = document.querySelector("#balanceSection .balance") as HTMLDivElement;
    try {
        const response: {
            status: string;
            user: User;
        } = await apiRequest("GET", "/user", data);

        let username: string;
        if (id) {
            username = response.user.name;
        }
        else {
            username = session.name;
        }

        balanceElement.innerText = `${username}'s Spaghetti: ${Number(response.user.balance).toFixed(2)}`;
    } catch (error) {
        balanceElement.innerText = `This account is private.`;
        renderErrorMessage(error);
    }
}


async function loadTransactions(id: string) {
    if (!id) {
        id = session.id;
    }
    const response: {
        status: string;
        transactions: Transaction[];
    } = await apiRequest("GET", "/transactions", { id });

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
        let accountId: string;
        let accountName: string;
        let amount: string;
        let direction: string;

        // Outbound
        if (transaction.source == id) {
            accountName = transaction.destinationName;
            accountId = transaction.destination;
            amount = "-" + Number(transaction.amount).toFixed(2);
            direction = "outbound";
        }
        // Inbound
        else {
            accountName = transaction.sourceName;
            accountId = transaction.source;
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
        if (accountId != "system") {
            transactionElement.querySelector(".account.field").addEventListener("click", () => {
                window.location.href = `/account?id=${accountId}`;
            });
        }
        highlight = !highlight;
    }
}
