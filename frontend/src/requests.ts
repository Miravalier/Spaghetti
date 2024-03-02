import { User, Friendship } from "./models.js";


class Session {
    token: string;
    id: string;
    name: string;
    user: User;

    constructor() {
        this.token = null;
        this.id = null;
        this.name = null;
        this.user = null;
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
            this.name = response.user.name;
            this.user = response.user;
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


export async function getFriendships(): Promise<Friendship[]> {
    const response: {
        status: string;
        outbound: { [id: string]: string };
        inbound: { [id: string]: string };
    } = await apiRequest("GET", "/friends");

    const friendships: Friendship[] = [];

    for (const [id, name] of Object.entries(response.outbound)) {
        if (response.inbound[id]) {
            delete response.inbound[id];
            friendships.push({ type: "completed", id, name });
        }
        else {
            friendships.push({ type: "outbound", id, name });
        }
    }
    for (const [id, name] of Object.entries(response.inbound)) {
        friendships.push({ type: "inbound", id, name });
    }
    return friendships;
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
