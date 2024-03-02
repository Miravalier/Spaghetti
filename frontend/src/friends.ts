import { apiRequest, getFriendships, session } from "./requests.js";
import { ButtonDialog, renderErrorMessage } from "./dialog.js";
import * as header from "./header.js";


window.addEventListener("load", async () => {
    await session.load();
    await render();
});


async function render() {
    console.log("[*] Rendering app");

    await header.render("Friends");

    const friendsList = document.createElement("div");
    friendsList.id = "friendsList";

    const addFriendButton = friendsList.appendChild(document.createElement("button"));
    addFriendButton.className = "add-friend";
    addFriendButton.textContent = "Add Friend";
    addFriendButton.addEventListener("click", async () => {
        const dialogResults = await new ButtonDialog(`
            <div class="field">
                <div class="label">User</div>
                <input name="user" type="text"></input>
            </div>
        `, ["Invite", "Cancel"]).render();

        if (dialogResults.button != "Invite") {
            return;
        }

        try {
            await apiRequest("POST", "/friend", { name: dialogResults.data.user });
        } catch (error) {
            const errorString: string = error.toString();
            renderErrorMessage(errorString);
        }
    });

    const requestSection = document.createElement("div");
    requestSection.className = "requests";
    requestSection.innerHTML = `<div class="label">Friend Requests</div>`;

    const friendSection = document.createElement("div");
    friendSection.className = "friends";
    friendSection.innerHTML = `<div class="label">Friends</div>`;

    let completedFriendships = false;
    let inboundRequests = false;

    for (const friendship of await getFriendships()) {
        console.log(friendship);
        const friendEntry = document.createElement("div");
        friendEntry.className = "friend";
        friendEntry.innerHTML = `
            <div class="name">${friendship.name}</div>
        `;
        friendEntry.querySelector(".name").addEventListener("click", () => {
            window.location.href = `/account?id=${friendship.id}`;
        });
        const entryButtons = friendEntry.appendChild(document.createElement("div"));
        entryButtons.className = "buttons";

        friendEntry.dataset.id = friendship.id;
        if (friendship.type == "completed") {
            friendSection.appendChild(friendEntry);
            friendEntry.classList.add("completed");
            completedFriendships = true;
        }
        else if (friendship.type == "inbound") {
            requestSection.appendChild(friendEntry);
            friendEntry.classList.add("request");
            inboundRequests = true;

            const acceptButton = entryButtons.appendChild(document.createElement("button"));
            acceptButton.className = "remove";
            acceptButton.innerText = "\u2713";
            acceptButton.addEventListener("click", async () => {
                await apiRequest("POST", "/friend", { name: friendship.name });
                window.location.reload();
            });
        }

        const removeButton = entryButtons.appendChild(document.createElement("button"));
        removeButton.className = "remove";
        removeButton.innerText = "X";
        removeButton.addEventListener("click", async () => {
            await apiRequest("DELETE", "/friend", { name: friendship.name });
            window.location.reload();
        });
    }

    if (!completedFriendships) {
        const notice = friendSection.appendChild(document.createElement("div"));
        notice.classList.add("notice");
        notice.innerText = "No friends added.";
    }

    if (inboundRequests) {
        friendsList.appendChild(requestSection);
    }
    friendsList.appendChild(friendSection);

    document.body.appendChild(friendsList);
}
