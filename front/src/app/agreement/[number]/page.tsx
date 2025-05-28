'use client';
import { callGetAgreement } from "@/components/api/agreementApi";
import { callGetInstallments } from "@/components/api/installmentApi";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import { Agreement, ApiResponse, Installment, PaginatedApiResponse } from "@/components/types";
import { useParams } from "next/navigation";
import { useContext, useEffect, useState } from "react";


export default function AgreementPage() {
    const { show } = useContext(SnackbarContext);
    const { number } = useParams();
    const [agreement, setAgreement] = useState<Agreement>(null as unknown as Agreement);
    const [installments, setInstallments] = useState<Installment[]>([]);

    useEffect(() => {
        async function callFetchAgreement() {
            if(!number) return;

            let agreement_response: ApiResponse<Agreement> = await callGetAgreement(number.toString());
            
            if(agreement_response.code !== 200) {
                show("Erro ao buscar acordo: " + agreement_response.message, "error");
                return;
            }
            setAgreement(agreement_response.data);
        }

        callFetchAgreement();
    }, [number]);

    useEffect(() => {
        async function callFetchInstallments() {
            let installments_response: PaginatedApiResponse<Installment> = await callGetInstallments(agreement.id);
            
            if(installments_response.code !== 200) {
                show("Erro ao buscar acordo: " + installments_response.message, "error");
                return;
            }

            setInstallments(installments_response.data.page.items);
        }
        
        if (!agreement || !agreement.id) return;
        callFetchInstallments();
    }, [agreement])

    return (
        <div className="flex flex-col gap-4 text-black justify-center items-center h-screen">
            <h1 className="text-4xl">Acordo {number}</h1>
            <span className="text-lg">Parcela {installments.length > 0 && installments[0].number}</span>
        </div>
    );

}