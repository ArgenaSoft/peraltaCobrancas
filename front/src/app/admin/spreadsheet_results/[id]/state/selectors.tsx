import { SpreadsheetState } from "./types";

export function selectPayersView(state: SpreadsheetState) {
  return Object.values(state.payers).map((payer) => ({
    ...payer,
    agreements: payer.agreementIds.map((aid) => {
      const agreement = state.agreements[aid];
      return {
        ...agreement,
        installments: agreement.installmentIds.map(
          (iid) => state.installments[iid]
        ),
      };
    }),
  }));
}

// export function selectCreditorsView(state: SpreadsheetState) {
//   return Object.values(state.creditors).map((creditor) => ({
// }