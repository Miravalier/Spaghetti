import { session } from "./requests.js";


const pages = ["Account", "Friends", "Settings", "About"];


export async function render(activePage: string) {
    const headerBar = document.createElement("div");
    headerBar.id = "headerBar";

    const pagesDiv = headerBar.appendChild(document.createElement("div"));
    pagesDiv.id = "pageLinks";
    for (const page of pages) {
        const aElement = pagesDiv.appendChild(document.createElement("a"));
        aElement.href = "/" + page.toLowerCase();
        if (page == activePage) {
            aElement.classList.add("selected");
        }
        aElement.innerText = page;
    }

    const profileDisplay = headerBar.appendChild(document.createElement("div"));
    profileDisplay.id = "profileDisplay";
    if (session.name && window.innerWidth >= 600) {
        profileDisplay.innerHTML = `User: <b>${session.name}</b>`;
        profileDisplay.addEventListener("click", () => {
            window.location.href = "/settings";
        });
    }

    document.body.prepend(headerBar);
}
