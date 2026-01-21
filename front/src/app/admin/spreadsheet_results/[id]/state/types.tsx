export type Id = string;

/* Entities */

export interface InstallmentEntity {
  id: Id; // agreementNumber-installmentNumber
  agreementId: Id;
  number: number;
  due_date: string;
  boletoPath?: string;
  readonly: boolean;
  deleted: boolean;
}

export interface AgreementEntity {
  id: Id; // agreement number
  payerId: Id; // cpf_cnpj
  creditor_name: string;
  installmentIds: Id[];
  readonly: boolean;
  deleted: boolean;
}

export interface PayerEntity {
  id: Id; // cpf_cnpj
  name: string;
  phone: string;
  agreementIds: Id[];
  readonly: boolean;
  deleted: boolean;
}

export interface CreditorEntity {
  id: Id; // name (idealmente outro id)
  name: string;
  reissue_margin: number;
  readonly: boolean;
  deleted: boolean;
}

/* Root state */

export interface SpreadsheetState {
  payers: Record<Id, PayerEntity>;
  agreements: Record<Id, AgreementEntity>;
  installments: Record<Id, InstallmentEntity>;
  creditors: Record<Id, CreditorEntity>;
  errors: string[];
  warnings: string[];
}
