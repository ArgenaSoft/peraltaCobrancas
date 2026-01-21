import { SpreadsheetDataSubmitPayload, SpreadsheetRetrieveResponse } from "@/components/api/returns/spreadsheetSchemas";
import { SpreadsheetState } from "./types";

export function normalizeSpreadsheet(
	dto: SpreadsheetRetrieveResponse
): SpreadsheetState {
	const state: SpreadsheetState = {
		payers: {},
		agreements: {},
		installments: {},
		creditors: {},
		errors: dto.errors,
		warnings: dto.warnings,
	};

	for (const creditor of dto.creditors) {
		state.creditors[creditor.name] = {
			id: creditor.name,
			name: creditor.name,
			reissue_margin: creditor.reissue_margin,
			readonly: creditor.readonly,
			deleted: false,
		};
	}

	for (const payer of dto.payers) {
		const payerId = payer.user.cpf_cnpj;

		state.payers[payerId] = {
			id: payerId,
			name: payer.name,
			phone: payer.phone,
			agreementIds: [],
			readonly: payer.readonly,
			deleted: false,
		};

		for (const agreement of payer.agreements) {
			state.agreements[agreement.number] = {
				id: agreement.number,
				payerId,
				creditor_name: agreement.creditor_name,
				installmentIds: [],
				readonly: agreement.readonly,
				deleted: false,
			};

			state.payers[payerId].agreementIds.push(agreement.number);

			for (const inst of agreement.installments) {
				const instId = `${agreement.number}-${inst.number}`;

				state.installments[instId] = {
					id: instId,
					agreementId: agreement.number,
					number: inst.number,
					due_date: inst.due_date,
					boletoPath: inst.boleto?.path,
					readonly: inst.readonly,
					deleted: false,
				};

				state.agreements[agreement.number].installmentIds.push(instId);
			}
		}
	}

	return state;
}


export function denormalizeSpreadsheet(
	state: SpreadsheetState
): SpreadsheetDataSubmitPayload {
	const dto: SpreadsheetDataSubmitPayload = {
		creditors: [],
		payers: []
	};

	for (const creditorName in state.creditors) {
		const creditor = state.creditors[creditorName];
		dto.creditors.push({
			name: creditor.name,
			reissue_margin: creditor.reissue_margin,
			readonly: creditor.readonly,
			deleted: creditor.deleted,
		});
	}

	for (const payerId in state.payers) {
		const payer = state.payers[payerId];
		const payerDto = {
			name: payer.name,
			user: {
				cpf_cnpj: payer.id,
				readonly: payer.readonly,
			},
			phone: payer.phone,
			agreements: [] as any[],
			readonly: payer.readonly,
			deleted: payer.deleted,
		};

		for (const agreementId of payer.agreementIds) {
			const agreement = state.agreements[agreementId];
			const agreementDto = {
				number: agreement.id,
				payer_cpf_cnpj: agreement.payerId,
				creditor_name: agreement.creditor_name,
				installments: [] as any[],
				readonly: agreement.readonly,
				deleted: agreement.deleted,
			};

			for (const instId of agreement.installmentIds) {
				const inst = state.installments[instId];
				const instDto = {
					agreement_num: inst.agreementId,
					number: inst.number,
					due_date: inst.due_date,
					boleto: inst.boletoPath
						? {
							path: inst.boletoPath,
							readonly: inst.readonly,
						}
						: undefined,
					readonly: inst.readonly,
					deleted: inst.deleted,
				};

				agreementDto.installments.push(instDto);
			}

			payerDto.agreements.push(agreementDto);
		}

		dto.payers.push(payerDto);
	}

	return dto;
}