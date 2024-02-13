class HeldLock {
    controller: AbortController

    constructor(controller: AbortController) {
        this.controller = controller;
    }

    release() {
        this.controller.abort();
    }
}

export class Lock {
    name: string;

    constructor() {
        this.name = crypto.randomUUID();
    }

    async acquireAndRun(callback: CallableFunction): Promise<any> {
        return await navigator.locks.request(this.name, async (lock) => {
            return await callback();
        });
    }

    async acquire(): Promise<HeldLock> {
        const controller = new AbortController();
        await new Promise<void>((heldResolve, heldReject) => {
            navigator.locks.request(this.name, async (lock) => {
                heldResolve();
                await new Promise<void>((releasedResolve, releasedReject) => {
                    controller.signal.addEventListener("abort", () => {
                        releasedResolve();
                    })
                });
            });
        });
        return new HeldLock(controller);
    }

    async tryAcquire(): Promise<HeldLock> {
        const controller = new AbortController();
        await new Promise<void>((heldResolve, heldReject) => {
            navigator.locks.request(this.name, { ifAvailable: true }, async (lock) => {
                if (!lock) {
                    heldReject(new Error("lock not available"));
                    return;
                }

                heldResolve();
                await new Promise<void>((releasedResolve, releasedReject) => {
                    controller.signal.addEventListener("abort", () => {
                        releasedResolve();
                    });
                });
            });
        });
        return new HeldLock(controller);
    }
}
