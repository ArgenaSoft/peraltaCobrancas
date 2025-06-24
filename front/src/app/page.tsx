'use client';
import { callGetHomeAgreements } from "@/components/api/agreementApi";
import { AuthContext } from "@/components/providers/authProvider";
import { HomeAgreement, Installment } from "@/components/types";
import { useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { readable_date, parseLocalDate } from "@/components/utils";

function AgreementComponent(agreement: Readonly<HomeAgreement>) {
  const router = useRouter();

  function handleAgreementClick() {
    router.push(`/agreement/${agreement.number}`);
  }

  const orderedInstallments = agreement.installments.toSorted(
    (a, b) => { return parseLocalDate(a.due_date).getTime() - parseLocalDate(b.due_date).getTime() }
  );


  // Sempre terá essa parcela pendente pois o backend só envia acordos abertos
  let lastPendingInstallment = orderedInstallments.find((installment) => installment.boleto.status === "pending") as Installment;
  let lastPendingInstallmentDate = parseLocalDate(lastPendingInstallment.due_date)
  let paidInstallmentsAmount = orderedInstallments.filter((installment) => installment.boleto.status === "paid").length;
  let isLate = lastPendingInstallmentDate < new Date();
  return (
    <div className={`flex flex-col rounded-2xl border-1 border-white p-2 ${isLate ? "bg-burnt-red" : ''}`}>
      <h3 className="text-xl">{agreement.creditor.name}</h3>
      <span className="text-md ml-4">Próxima parcela: {readable_date(lastPendingInstallmentDate)}</span>
      <span className="text-sm ml-4 opacity-50">{paidInstallmentsAmount} de {agreement.installments.length} parcelas</span>
      <span className="text-lg self-end cursor-pointer" onClick={handleAgreementClick}>Ver acordo -&gt;</span>
    </div>
  );
}

export default function HomePage() {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [agreements, setAgreements] = useState<HomeAgreement[]>([] as any);

  useEffect(() => {
    setLoading(true);
    async function getAgreements() {
      let response = await callGetHomeAgreements();
      if (response.code === 200) {
        setAgreements(response.data);
      } else {
        console.log("Erro ao buscar acordos:", response.message);
      }
      setLoading(false);
    }

    getAgreements();
  }, []);

  if (loading) {
    return <></>
  }

  return (
    <div>
      <h1 className="text-black text-4xl mb-10">Olá, {user?.username}</h1>
      <div className="bg-dark-blue rounded-2xl">
        {agreements.length > 0 ? (
          <div className="flex flex-col p-4 gap-4 text-white">
            <h2 className="font-bold">Acordos ativos</h2>
            {agreements.map((agreement) => {
              return (
                <div key={agreement.number}>
                  <AgreementComponent {...agreement} />
                </div>
              );
            }
            )}
          </div>
        )
      :
      <div>
        <h2 className="font-bold text-3xl">Você não possui acordos ativos</h2>
      </div>
      }
      </div>
    </div>
  );
}