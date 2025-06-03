'use client';
import { callGetAgreement } from "@/components/api/agreementApi";
import { callGetInstallments } from "@/components/api/installmentApi";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import { Agreement, ApiResponse, Installment, PaginatedApiResponse } from "@/components/types";
import { readable_date } from "@/components/utils";
import { useParams, useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";


export default function AgreementPage() {
    const router = useRouter();
    const { show } = useContext(SnackbarContext);
    const { number } = useParams();
    const [agreement, setAgreement] = useState<Agreement>(null as unknown as Agreement);
    const [openedInstallments, setOpenedInstallments] = useState<number[]>([]);

    useEffect(() => {
        // Busca o acordo
        async function callFetchAgreement() {
            if (!number) return;

            let agreement_response: ApiResponse<Agreement> = await callGetAgreement(number.toString());

            if (agreement_response.code !== 200) {
                show("Erro ao buscar acordo: " + agreement_response.message, "error");
                router.push("/");
            }
            setAgreement(agreement_response.data);
        }

        callFetchAgreement();
    }, [number]);

    useEffect(() => {
        // Quando o acordo for carregado, vou buscar as parcelas
        async function callFetchInstallments() {
            let installments_response: PaginatedApiResponse<Installment> =
                await callGetInstallments(
                    agreement.id,
                    true
                );

            if (installments_response.code !== 200) {
                show("Erro ao buscar acordo: " + installments_response.message, "error");
                return;
            }

            let installments = installments_response.data.page.items;
            // Ordena as parcelas por vencimento
            installments.sort((a, b) => {
                return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
            });

            setAgreement({
                ...agreement,
                installments: installments
            });
        }

        if (!agreement || !agreement.id) return;
        callFetchInstallments();
    }, [agreement?.id]);

    useEffect(() => {
        // Quando as parcelas forem carregadas, vou ver quais já devem estar abertas
        if(agreement){
            let opened = agreement.installments.filter(installment => installment.boleto.status === "pending").map(installment => installment.number);
            setOpenedInstallments(opened);
        }

    }, [agreement?.installments]);

    function switchOpenInstallment(installmentNumber: number) {
        if (openedInstallments.includes(installmentNumber)) {
            setOpenedInstallments(openedInstallments.filter(num => num !== installmentNumber));
        } else {
            setOpenedInstallments([...openedInstallments, installmentNumber]);
        }
    }


    if (!agreement || !agreement.id || !agreement.installments) {
        return (
            <div className="flex flex-col gap-4 text-black justify-center items-center h-screen">
                <h1 className="text-4xl">Carregando acordo...</h1>
                <h2 className="text-lg opacity-50">Sinistro {number}</h2>
                <h2 className="text-lg opacity-50">Aguarde um momento</h2>
            </div>
        )
    }

    console.log(agreement.installments);
    return (
        <div className="flex flex-col text-black justify-center items-start">
            <h1 className="text-4xl mb-3">Acordo com <strong>{agreement.creditor.name}</strong></h1>
            <h2 className="text-lg opacity-50">Sinistro {number}</h2>
            <h2 className="text-lg opacity-50">{agreement.installments.length} parcelas</h2>
            <div className="flex flex-col gap-4 mt-4 w-full">
                {agreement.installments.slice().reverse().map((installment, index) => {
                    index = agreement.installments.length - index; // Inverte o índice

                    let isOpened = openedInstallments.includes(installment.number);
                    let isPending = installment.boleto.status === "pending";
                    let isLate = new Date(installment.due_date) < new Date() && isPending;

                    let backgroundColor = 'bg-gray-300';
                    let textColor = 'text-gray-500';
                    let linkColor = 'text-anchor-blue';
                    if (isPending) {
                        backgroundColor = isLate ? 'bg-burnt-red' : 'bg-dark-blue';
                        textColor = 'text-white';
                        linkColor = 'text-anchor-blue-light';
                    }

                    return (
                        <div 
                        key={installment.number} 
                        onClick={() => switchOpenInstallment(installment.number)}
                        className={`flex flex-col ${backgroundColor} ${textColor} rounded-lg w-full p-2 px-4`}>
                            <div className="flex justify-between">
                                <h3 className="text-xl">Nº: {index}</h3>
                                <p>Vencimento: {readable_date(installment.due_date)}</p>
                                { installment.boleto && 
                                    <a className={`${linkColor} underline`} href="">Ver boleto</a>
                                }
                            </div>

                            {isOpened && (
                                <div className="mt-4">
                                    <p>ASD</p>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    );
}