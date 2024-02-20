export type User = {
    id: string;
    name: string;
    admin: boolean;
    balance: string;
};


export type Transaction = {
    id: string;
    source: string;
    destination: string;
    amount: string;
    date: string;
    comment: string;
};
