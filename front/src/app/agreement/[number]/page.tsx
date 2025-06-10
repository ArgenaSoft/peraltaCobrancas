'use client';
import { callGetAgreement } from "@/components/api/agreementApi";
import { callGetInstallments } from "@/components/api/installmentApi";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import { Agreement, ApiResponse, Installment, PaginatedApiResponse } from "@/components/types";
import { readable_date } from "@/components/utils";
import { faChevronDown, faChevronUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useParams, useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";
import { faWhatsapp } from '@fortawesome/free-brands-svg-icons'


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
            console.log(installments)

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
            let opened = agreement.installments.filter(
                (installment) => {
                    if(installment.boleto === null) return false;
                    return installment.boleto.status === "pending"
                }
            ).map(installment => installment.number);
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

    function getPdfUrl(uri: string): string {
        if (!uri) return "";
        return process.env.NEXT_PUBLIC_API_URL + uri;
    }

    function getMoreInfoWppUrl(agreement: Agreement, installment: Installment): string {
        if (!agreement || !installment || !installment.boleto) return "";
        let creditor = agreement.creditor.name;
        let message = `Olá, gostaria de saber mais sobre o boleto do acordo com ${creditor} parcela ${installment.number}.`;

        return `https://wa.me/${process.env.NEXT_PUBLIC_WPP_NUMBER}?text=${encodeURIComponent(message)}`;
    }

    function getReissueWppUrl(agreement: Agreement, installment: Installment): string {
        if (!agreement || !installment || !installment.boleto) return "";
        let creditor = agreement.creditor.name;
        let message = `Olá, gostaria de reemitir o boleto do acordo com ${creditor} parcela ${installment.number}.`;

        return `https://wa.me/${process.env.NEXT_PUBLIC_WPP_NUMBER}?text=${encodeURIComponent(message)}`;
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

    let now = new Date();
    return (
        <div className="flex flex-col text-black justify-center items-start">
            <h1 className="text-4xl mb-3">Acordo com <strong>{agreement.creditor.name}</strong></h1>
            <h2 className="text-lg opacity-50">Sinistro {number}</h2>
            <h2 className="text-lg opacity-50">{agreement.installments.length} parcelas</h2>
            <div className="flex flex-col gap-4 mt-4 w-full">
                {agreement.installments.slice().reverse().map((installment, index) => {
                    index = agreement.installments.length - index; // Inverte o índice

                    let isOpened = openedInstallments.includes(installment.number);
                    let backgroundColor = 'bg-gray-300';
                    let textColor = 'text-gray-500';
                    let linkColor = 'text-anchor-blue';
                    let isLate = false;
                    let isPending = false;
                    let crossedReissueMargin = false;
                    let dueDate = new Date(installment.due_date);

                    if(installment.boleto){
                        isPending = installment.boleto.status === "pending";
                        isLate = dueDate < now && isPending;
                        // agreement.creditor.reissue_margin  é um inteiro indicando o número de dias antes do vencimento quando o boleto já deve ser reemitido
                        if(isLate && (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24) <= agreement.creditor.reissue_margin){
                            crossedReissueMargin = true;
                        }

                        if (isPending) {
                            backgroundColor = isLate ? 'bg-burnt-red' : 'bg-dark-blue';
                            textColor = 'text-white';
                            linkColor = 'text-anchor-blue-light';
                        }
                    }

                    let wppLink = crossedReissueMargin ? getReissueWppUrl(agreement, installment) : getMoreInfoWppUrl(agreement, installment);
                    let wppLabel = crossedReissueMargin ? "Reemitir via Whatsapp" : "Pedir via Whatsapp";


                    return (
                        <div 
                        key={installment.number} 
                        onClick={() => switchOpenInstallment(installment.number)}
                        className={`flex flex-col ${backgroundColor} ${textColor} rounded-lg w-full p-2 px-4`}>
                            <div className="flex flex-wrap justify-between">
                                <h3 className="text-xl">Nº: {index}</h3>
                                <p>Vencimento: {readable_date(installment.due_date)}</p>
                                <FontAwesomeIcon icon={isOpened ? faChevronUp : faChevronDown} className="cursor-pointer" />
                            </div>

                            {isOpened && (
                                <div className="mt-4">
                                    { installment.boleto && 
                                    <div className={`flex justify-between items-center ${linkColor}`}>
                                        <a className="underline" href={getPdfUrl(installment.boleto.pdf)}>Ver boleto</a>
                                        <a className="flex justify-between items-center gap-2" href={wppLink}>
                                            <FontAwesomeIcon icon={faWhatsapp} className="text-green-500 text-3xl"/>
                                            <span>{wppLabel}</span>
                                        </a>
                                    </div>
                                }
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    );
}