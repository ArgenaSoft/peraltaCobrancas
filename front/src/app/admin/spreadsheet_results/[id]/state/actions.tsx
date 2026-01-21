import { SpreadsheetState, Id } from "./types";

type Setter = React.Dispatch<React.SetStateAction<SpreadsheetState | null>>;


function changePayer(set: Setter, id: Id, state: boolean) {
    set((prev) => {
        if (!prev) return prev;
        return {
            ...prev,
            payers: {
                ...prev.payers,
                [id]: { ...prev.payers[id], deleted: state },
            },
        };
    });
}

export function deletePayer(set: Setter, id: Id) {
    changePayer(set, id, true);
}

export function revertPayer(set: Setter, id: Id) {
    changePayer(set, id, false);
}

function changeAgreement(set: Setter, id: Id, state: boolean) {
    set((prev) => {
        if (!prev) return prev;

        return {
        ...prev,
        agreements: {
            ...prev.agreements,
            [id]: { ...prev.agreements[id], deleted: state },
        },
    }});
}

export function deleteAgreement(set: Setter, id: Id) {
    changeAgreement(set, id, true);
}

export function revertAgreement(set: Setter, id: Id) {
    changeAgreement(set, id, false);
}

function changeInstallment(set: Setter, id: Id, state: boolean) {
    set((prev) => {
        if (!prev) return prev;

        return {
        ...prev,
        installments: {
            ...prev.installments,
            [id]: { ...prev.installments[id], deleted: state },
        },
    }});
}

export function deleteInstallment(set: Setter, id: Id) {
    changeInstallment(set, id, true);
}

export function revertInstallment(set: Setter, id: Id) {
    changeInstallment(set, id, false);
}

function changeCreditor(set: Setter, id: Id, state: boolean) {
    set((prev) => {
        if (!prev) return prev;
        return {
        ...prev,
        creditors: {
            ...prev.creditors,
            [id]: { ...prev.creditors[id], deleted: state },
        },
    }});
}

export function deleteCreditor(set: Setter, id: Id) {
    changeCreditor(set, id, true);
}

export function revertCreditor(set: Setter, id: Id) {
    changeCreditor(set, id, false);
}