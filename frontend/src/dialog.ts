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
    focusButton: HTMLButtonElement;

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

        const updateResultData = (element: HTMLInputElement | HTMLSelectElement) => {
            if (element.type == "number") {
                results.data[element.name] = Number(element.value);
            } else {
                results.data[element.name] = element.value;
            }
        };

        for (const input of this.container.querySelectorAll<HTMLInputElement>("input")) {
            if (!input.name) {
                continue;
            }
            updateResultData(input);
            input.addEventListener("change", () => updateResultData(input));
        }

        for (const select of this.container.querySelectorAll<HTMLSelectElement>("select")) {
            if (!select.name) {
                continue;
            }
            updateResultData(select);
            select.addEventListener("change", () => updateResultData(select));
        }

        let firstButton = true;
        for (const button of this.container.querySelectorAll<HTMLButtonElement>(".buttons button")) {
            if (firstButton) {
                this.focusButton = button;
                firstButton = false;
            }
            button.addEventListener("click", () => {
                results.button = button.dataset.id;
                this.future.resolve(results);
                this.close();
            });
        }
    }

    render(): this {
        const x = super.render();
        x.focusButton.focus();
        return x;
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


export async function renderErrorMessage(details: string) {
    return await new ButtonDialog(`
        <h4>\u26A0\uFE0F Error</h4>
        <div class="error">
            ${details}
        </div>
    `, ["Ok"]).render();
}
