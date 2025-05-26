interface UserType {
    access: string;
    refresh: string;
    username: string;
};

interface Creditor {
    name: string;
}

interface Boleto {
    due_date: string;
    status: "pending" | "paid";
}

interface Installment {
    id: number;
    boleto: Boleto;
}

interface Agreement {
    id: number;
    creditor: Creditor;
    installments: Installment[];
}

    export type { UserType, Creditor, Installment, Agreement }; 