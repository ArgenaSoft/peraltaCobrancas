'use client';
import { callGetAgreements } from "@/components/api/agreementApi";
import { AuthContext } from "@/components/providers/authProvider";
import { Agreement, Installment } from "@/components/types";
import { useContext, useEffect, useState } from "react";
import { format } from 'date-fns';
import { useRouter } from "next/navigation";

function AgreementComponent(agreement: Readonly<Agreement>) {
  const router = useRouter();
  
  function handleAgreementClick(){
    router.push(`/agreement/${agreement.number}`);
  }

  const orderedInstallments = agreement.installments.toSorted(
    (a, b) => new Date(a.boleto.due_date).getTime() - new Date(b.boleto.due_date).getTime()
  );

  // Sempre terá essa parcela pendente pois o backend só envia acordos abertos
  let lastPendingInstallment = orderedInstallments.find((installment) => installment.boleto.status === "pending") as Installment;
  let lastPendingInstallmentDate = new Date(lastPendingInstallment.boleto.due_date)

  let paidInstallmentsAmount = orderedInstallments.filter((installment) => installment.boleto.status === "paid").length;
  let isLate = lastPendingInstallmentDate < new Date();
  return(
    <div className={`flex flex-col rounded-2xl border-1 border-white p-2 ${isLate ? "bg-burnt-red" : ''}`}>
      <h3 className="text-xl">{agreement.creditor.name}</h3>
      <span className="text-md ml-4">Próxima parcela: {format(lastPendingInstallmentDate, 'dd/MM/yyyy')}</span>
      <span className="text-sm ml-4 opacity-50">{paidInstallmentsAmount} de {agreement.installments.length} parcelas</span>
      <span className="text-lg self-end" onClick={handleAgreementClick}>Ver acordo -&gt;</span>
    </div>
  );
}

export default function HomePage() {
  const { user } = useContext(AuthContext);
  const [agreements, setAgreements] = useState<Agreement[]>([] as any);


  useEffect(() => {
    async function getAgreements() {
      let response = await callGetAgreements();
      console.log(response);
      if (response.code === 200) {
        setAgreements(response.data);
      } else {
        console.error("Erro ao buscar acordos:", response.message);
      }
    }

    getAgreements();
  }, []);

  return(
    <div>
      <h1 className="text-black text-4xl mb-10">Olá, {user?.username}</h1>
      {agreements.length > 0 && (
        <div className="flex flex-col bg-dark-blue rounded-2xl p-4 gap-4">
          <h2 className="font-bold text-3xl">Acordos ativos</h2>
          {agreements.map((agreement) => {

            return (
              <div key={agreement.number}>
                <AgreementComponent {...agreement} />
              </div>
            );
          }
          )}
        </div>
      )}
    </div>
  );
}