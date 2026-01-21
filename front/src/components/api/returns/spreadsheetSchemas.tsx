export interface BoletoResponse {
  path: string;
  readonly: boolean;
}

export interface InstallmentResponse {
  agreement_num: string;
  number: number;
  due_date: string;
  boleto: BoletoResponse | null;
  readonly: boolean;
}

export interface InstallmentPayload {
  agreement_num: string;
  number: number;
  due_date: string;
  boleto: BoletoResponse | null;
  readonly: boolean;
  deleted: boolean;
}

export interface AgreementPayload {
  number: string;
  payer_cpf_cnpj: string;
  creditor_name: string;
  installments: InstallmentPayload[];
  readonly: boolean;
  deleted: boolean;
}

export interface AgreementResponse {
  number: string;
  payer_cpf_cnpj: string;
  creditor_name: string;
  installments: InstallmentResponse[];
  readonly: boolean;
}

export interface UserResponse {
  cpf_cnpj: string;
  readonly: boolean;
}

export interface PayerPayload {
  name: string;
  user: UserResponse;
  phone: string;
  agreements: AgreementPayload[];
  readonly: boolean;
  deleted: boolean;
}

export interface PayerResponse {
  name: string;
  user: UserResponse;
  phone: string;
  agreements: AgreementResponse[];
  readonly: boolean;
}

export interface CreditorResponse {
  name: string;
  reissue_margin: number;
  readonly: boolean;
}

export interface CreditorPayload {
  name: string;
  reissue_margin: number;
  readonly: boolean;
  deleted: boolean;
}

export interface SpreadsheetRetrieveResponse {
  creditors: CreditorResponse[];
  payers: PayerResponse[];
  errors: string[];
  warnings: string[];
}


export interface SpreadsheetSubmitResponse {
  job_id: string;
}

export interface SpreadsheetDataSubmitPayload {
  creditors: CreditorPayload[];
  payers: PayerPayload[];
}

export interface SpreadsheetDataSubmitResponse {
  success: boolean;
}