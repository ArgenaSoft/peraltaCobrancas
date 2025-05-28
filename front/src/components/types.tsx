export type ApiResponse<T = Record<string, unknown>> = {
  code: number;
  message: string | null;
  data: T | null;
};

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
    number: number;
    boleto: Boleto;
}

interface Agreement {
    number: number;
    creditor: Creditor;
    installments: Installment[];
}

    export type { UserType, Creditor, Installment, Agreement }; 