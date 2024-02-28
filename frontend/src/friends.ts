import { apiRequest, getFriendships, session } from "./requests.js";
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
    addFriendButton.addEventListener("click", () => {
        console.log("asdf");
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
        const friendEntry = document.createElement("div");
        friendEntry.className = "friend";
        friendEntry.innerHTML = `<div class="name">${friendship.name}</div>`;
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
        }
    }

    for (let i = 0; i < 100; i++) {
        const friendEntry = document.createElement("div");
        friendEntry.className = "friend";
        friendEntry.innerHTML = `<div class="name">Asdf</div>`;
        friendEntry.dataset.id = "aaa";

        friendSection.appendChild(friendEntry);
        friendEntry.classList.add("completed");
        completedFriendships = true;
    }

    if (inboundRequests) {
        friendsList.appendChild(requestSection);
    }
    friendsList.appendChild(friendSection);

    document.body.appendChild(friendsList);
}
