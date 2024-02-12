import { session } from "./session.js";


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
