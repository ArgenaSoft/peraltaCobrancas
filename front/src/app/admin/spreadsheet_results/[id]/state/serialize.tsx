import { SpreadsheetState } from "./types";

export function serializeForSubmit(state: SpreadsheetState) {
  return {
    removed: {
      payers: Object.values(state.payers)
        .filter((p) => p.deleted && !p.readonly)
        .map((p) => p.id),

      agreements: Object.values(state.agreements)
        .filter((a) => a.deleted && !a.readonly)
        .map((a) => a.id),

      installments: Object.values(state.installments)
        .filter((i) => i.deleted && !i.readonly)
        .map((i) => i.id),
    },
  };
}
