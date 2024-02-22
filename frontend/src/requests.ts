import { User } from "./models.js";


class Session {
    token: string;
    id: string;

    constructor() {
        this.token = null;
        this.id = null;
    }

    async load() {
        // Try to grab the token from storage
        this.token = localStorage.getItem("token");
        if (this.token == null) {
            window.location.href = "/login";
        }

        // Try to make a status request with this token
        try {
            const response: {
                status: string;
                user: User;
            } = await apiRequest("GET", "/status");
            this.id = response.user.id;
        } catch (error) {
            window.location.href = "/login";
        }
    }
}


export const session = new Session();


export async function apiRequest(method: string, endpoint: string, data: any = null): Promise<any> {
    const parameters: RequestInit = {
        method,
        cache: "no-cache",
        headers: {},
    };
    let url = `/api${endpoint}`;
    if (session.token !== null) {
        parameters.headers["Authorization"] = `Bearer ${session.token}`;
    }
    if (data !== null) {
        if (method == "POST" || method == "PUT") {
            parameters.headers["Content-Type"] = "application/json";
            parameters.body = JSON.stringify(data);
        }
        else {
            const queryParams = [];
            for (let [key, value] of Object.entries(data)) {
                queryParams.push(`${key}=${value}`);
            }
            url += "?" + queryParams.join("&");
        }
    }
    const response = await fetch(url, parameters);
    if (response.status != 200) {
        let error: Error;
        try {
            error = Error((await response.json()).detail);
        } catch (error) {
            error = new Error(await response.text());
        }
        throw error;
    }
    return await response.json();
}


export async function getUserById(id: string): Promise<User> {
    const response: {
        status: string;
        user: User;
    } = await apiRequest("GET", "/user", { id });
    return response.user;
}


export async function getUserByName(name: string): Promise<User> {
    const response: {
        status: string;
        user: User;
    } = await apiRequest("GET", "/user", { name });
    return response.user;
}
