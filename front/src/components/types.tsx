type ApiResponse<T = Record<string, unknown>> = {
  code: number;
  message: string | null;
  data: T;
};

type Page<T = Record<string, unknown>> = {
    items: T[];
    page: number;
}

type Paginator = {
    page_size: number;
    total_items: number;
    total_pages: number;
}

type PaginatedApiResponse<T = Record<string, unknown>> = {
  code: number;
  message: string | null;
  data: {
    page: Page<T>;
    paginator: Paginator;
  }
};

interface UserTokens {
    access: string;
    refresh: string;
    username: string;
};

interface Creditor {
    name: string;
    reissue_margin: number;
}

interface Boleto {
    status: "pending" | "paid";
    pdf: string;
}

interface Installment {
    number: number;
    boleto: Boleto;
    due_date: string;
}

interface HomeAgreement {
    id: number;
    number: number;
    creditor: Creditor;
    installments: Installment[];
}

interface User {
    id: number;
    cpf: string;
}

interface Payer {
    id: number;
    name: string;
    phone: string;
    user: User;
}

interface Agreement {
    id: number;
    number: string;
    creditor: Creditor;
    payer: Payer;
    installments: Installment[];
}

export type { UserTokens, Creditor, Installment, HomeAgreement, Agreement, ApiResponse, PaginatedApiResponse, Paginator, Page, Boleto, User, Payer };