import { Future } from "./futures.js";


export class Dialog {
    container: HTMLDivElement;

    constructor(contents: string) {
        this.container = document.createElement("div");
        this.container.className = "dialog-container";
        this.container.innerHTML = `
            <div class="dialog">
                ${contents}
            </div>
        `;
        this.container.addEventListener("click", (ev) => {
            ev.stopPropagation();
            this.close();
        });
        this.container.querySelector<HTMLDivElement>(".dialog").addEventListener("click", (ev) => {
            ev.stopPropagation();
        });
    }

    render(): this {
        document.body.appendChild(this.container);
        return this;
    }

    close() {
        this.container.remove();
    }
}


export class ButtonDialog extends Dialog {
    future: Future<string>;

    constructor(contents: string, buttons: string[]) {
        let buttonContents = "";
        for (const button of buttons) {
            buttonContents += `<button type="button" data-id="${button}">${button}</button>`;
        }

        super(`
            ${contents}
            <div class="buttons">
                ${buttonContents}
            </div>
        `);

        this.future = new Future<string>();

        this.container.addEventListener("click", (ev) => {
            ev.stopPropagation();
            this.close();
        });

        for (const button of this.container.querySelectorAll<HTMLButtonElement>(".buttons button")) {
            button.addEventListener("click", () => {
                this.future.resolve(button.dataset.id);
                this.close();
            });
        }
    }

    close() {
        this.future.reject(new Error("dialog closed"));
        super.close();
    }

    then(onfulfilled?: (value: string) => string | PromiseLike<string>,
        onrejected?: (reason: any) => PromiseLike<never>) {
        return this.future.then(onfulfilled, onrejected);
    }
}
