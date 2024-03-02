export type Privacy = "public" | "friends" | "private";


export type User = {
    id: string;
    name: string;
    admin: boolean;
    balance: string;
    privacy: Privacy;
};


export type Transaction = {
    id: string;
    source: string;
    sourceName: string;
    destination: string;
    destinationName: string;
    amount: string;
    date: string;
    comment: string;
};


export type FriendshipType = "completed" | "inbound" | "outbound";


export type Friendship = {
    type: FriendshipType;
    id: string;
    name: string;
};
