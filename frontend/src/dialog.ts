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


export type ButtonDialogResults = {
    button: string;
    data: any;
};


export class ButtonDialog extends Dialog {
    future: Future<ButtonDialogResults>;

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

        this.future = new Future<ButtonDialogResults>();
        const results: ButtonDialogResults = { button: "", data: {} };

        this.container.addEventListener("click", (ev) => {
            ev.stopPropagation();
            this.close();
        });

        for (const input of this.container.querySelectorAll<HTMLInputElement>("input")) {
            if (!input.name) {
                continue;
            }
            const updateResultData = () => {
                if (input.type == "number") {
                    results.data[input.name] = Number(input.value);
                } else {
                    results.data[input.name] = input.value;
                }
            };
            updateResultData();
            input.addEventListener("change", updateResultData);
        }

        for (const button of this.container.querySelectorAll<HTMLButtonElement>(".buttons button")) {
            button.addEventListener("click", () => {
                results.button = button.dataset.id;
                this.future.resolve(results);
                this.close();
            });
        }
    }

    close() {
        this.future.reject(new Error("dialog closed"));
        super.close();
    }

    then(onfulfilled?: (value: ButtonDialogResults) => ButtonDialogResults | PromiseLike<ButtonDialogResults>,
        onrejected?: (reason: any) => PromiseLike<never>) {
        return this.future.then(onfulfilled, onrejected);
    }
}
