import * as header from "./header.js";


window.addEventListener("load", async () => {
    await render();
});


async function render() {
    console.log("[*] Rendering app");
    await header.render("About");
}
