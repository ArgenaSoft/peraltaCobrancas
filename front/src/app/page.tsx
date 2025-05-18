'use client';
import { AuthContext } from "@/components/providers/authProvider";
import { useContext } from "react";

export default function Home() {
  const { user } = useContext(AuthContext);
  const agreements = [
    {
      id: 1,
      creditor: {
        name: "Companhia EtC",
      },
      installments: [
        {
          id: 1,
          dueDate: "2025-05-01",
          amount: 100,
          status: "pending",
        },
        {
          id: 2,
          dueDate: "2025-06-01",
          amount: 100,
          status: "pending",
        }
      ]
    },
    {
      id: 2,
      creditor: {
        name: "Companhia EtC",
      },
      installments: [
        {
          id: 1,
          dueDate: "2025-05-01",
          amount: 100,
          status: "paid",
        },
        {
          id: 3,
          dueDate: "2025-07-01",
          amount: 100,
          status: "pending",
        },
        {
          id: 2,
          dueDate: "2025-06-01",
          amount: 100,
          status: "pending",
        },
      ]
    }
  ]

  return(
    <div>
      <h1 className="text-black text-3xl mb-10">Olá, {user?.username}</h1>

      <div className="flex flex-col bg-dark-blue rounded-2xl p-4 gap-4">
        <h2 className="font-bold text-2xl">Acordos ativos</h2>
        {agreements.map((agreement) => {
          const orderedInstallments = agreement.installments.toSorted(
            (a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
          );
          let lastPendingInstallment = orderedInstallments.find((installment) => installment.status === "pending");
          let lastPendingInstallmentIndex = orderedInstallments.indexOf(lastPendingInstallment);
          let paidInstallmentsAmount = orderedInstallments.filter((installment) => installment.status === "paid").length;
          let isLate = new Date(lastPendingInstallment.dueDate) < new Date();

          return (<div key={agreement.id} className={`flex flex-col rounded-2xl border-1 border-white p-4 ${isLate ? "bg-burnt-red" : ''}`}>
            <h3 className="text-xl">{agreement.creditor.name}</h3>
            <span className="text-md ml-4">Próxima parcela: {lastPendingInstallment.dueDate}</span>
            <span className="text-sm ml-4 opacity-50">{paidInstallmentsAmount} de {agreement.installments.length} parcelas</span>
            <span className="text-lg self-end">Ver acordo -&gt;</span>
          </div>)
        }
        )}
      </div>
    </div>
  );
}