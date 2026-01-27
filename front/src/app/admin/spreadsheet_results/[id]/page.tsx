'use client';

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { callGetResults, callSaveSpreadsheetResults } from "@/components/api/spreadsheetApi";
import { ApiResponse } from "@/components/types";
import { SpreadsheetRetrieveResponse } from "@/components/api/returns/spreadsheetSchemas";

import { SpreadsheetState } from "./state/types";
import { normalizeSpreadsheet, denormalizeSpreadsheet } from "./state/adaptors";
import { selectPayersView } from "./state/selectors";
import {
  deletePayer,
  revertPayer,
  deleteAgreement,
  deleteInstallment,
  revertAgreement,
  revertInstallment,
  deleteCreditor,
  revertCreditor
} from "./state/actions";

import { DeleteRevertButton } from "./components"
import { emitSnack } from "@/components/snackEmitter";

export default function SpreadsheetResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<SpreadsheetState | null>(null);
  const router = useRouter();

  /* Load */
  useEffect(() => {
    async function load() {
      const response: ApiResponse<SpreadsheetRetrieveResponse> =
        await callGetResults(id);

      if (!response.data) {
        setState(null);
        return;
      }
      setState(normalizeSpreadsheet(response.data));
    }
    
    load();
  }, [id]);

  async function sendData() {
    if (!state) return;

    const response = await callSaveSpreadsheetResults(id, denormalizeSpreadsheet(state));
    if (response.code != 200) {
      console.error("Error updating results:", response.message);
      emitSnack("Erro", response.message ?? "Erro ao salvar dados.","error");
      return;
    }

    router.push("/admin");
  }

  /* Payers View model */
  const payers = useMemo(
    () => (state ? selectPayersView(state) : []),
    [state]
  );

  if (!state) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="text-black flex flex-col items-center justify-center p-2 gap-10">
        <h1 className="text-[35px]">Confirmar dados</h1>

        <div id="payers-list" className="flex flex-col gap-4 items-center">
          <h2 className="text-[25px]">Pagadores e acordos</h2>
          {payers.map((payer) => (
              <div key={payer.id} 
                className={`rounded-2xl bg-dark-blue flex flex-col border-2 
                border-dark-blue overflow-clip w-full max-w-[80vw]`}>

              {/* Cabeçalho */}
              <div className="flex justify-around items-center bg-white p-2">
                <span className={`basis-2/3 text-[15px] ${payer.deleted ? "line-through opacity-20" : ""}`}>{payer.name}</span>

                <DeleteRevertButton item={payer} 
                  onDelete={() => deletePayer(setState, payer.id)} 
                  onRevert={() => revertPayer(setState, payer.id)}
                  enabled={true}
                  />
              </div>

              {/* Corpo */}
              <div className={`p-4 flex flex-col gap-4 text-white overflow-hidden ${payer.deleted ? "opacity-20" : ""}`}>
                {payer.agreements.map((agreement) => (
                  <div key={agreement.id} className={`flex flex-col`}>
                    <div className="flex items-center overflow-hidden">
                      <span 
                        className={
                          `mr-2 overflow-hidden flex-1 min-w-0 text-ellipsis 
                          active:relative active:min-w-fit whitespace-nowrap 
                          ${agreement.deleted ? "line-through opacity-20" : ""}`
                        }>Acordo {agreement.id}</span>

                      <DeleteRevertButton item={agreement} 
                        onDelete={() => deleteAgreement(setState, agreement.id)} 
                        onRevert={() => revertAgreement(setState, agreement.id)}
                        enabled={!payer.deleted}
                        />

                    </div>
                    <div className={`${agreement.deleted ? "opacity-20" : ""} flex flex-col mt-2`}>
                      {agreement.installments.map((inst) => (
                        <div key={inst.id} className={`flex items-center border-l-2 border-white px-2 ml-2`}>
                          <span className={`mr-2 w-20 ${inst.deleted ? "line-through opacity-20" : ""}`}>Parcela {inst.number}</span>

                          <DeleteRevertButton item={inst}
                            onDelete={() => deleteInstallment(setState, inst.id)} 
                            onRevert={() => revertInstallment(setState, inst.id)}
                            enabled={!payer.deleted && !agreement.deleted}
                            />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        {
          Object.values(state.creditors).length > 0 && 
          <div id="creditors-list" className="flex flex-col gap-4 items-center">
            <h2 className="text-[25px]">Credores</h2>
            <span className="italic text-[15px] text-justify">Remover um credor também removerá todos os acordos e parcelas associados a ele (após submissão). O pagador só será removido junto se tiver acordos apenas com o credor removido.</span>
            {Object.values(state.creditors).map((creditor) => (
              <div key={creditor.id} className="flex p-2 border-b-2 border-black w-full justify-between">
                <span className="text-[20px]">{creditor.name}</span>
                <DeleteRevertButton item={creditor}
                  onDelete={() => deleteCreditor(setState, creditor.id)} 
                  onRevert={() => revertCreditor(setState, creditor.id)}
                  enabled={true}
                  />
              </div>
            ))}
          </div>
        }

      </div>
      <div id="buttons" className="flex justify-between w-full sticky bottom-0 left-0 rounded-t-2xl border-b-0 border-2 border-dark-blue bg-white shadow-2xl p-4">
        <button className="bg-white text-dark-blue border-2 border-dark-blue p-3 rounded-lg mx-2 cursor-pointer"
          onClick={()=>{router.push("/admin")}}
        >Cancelar</button>
        <button className="bg-dark-blue text-white p-3 rounded-lg mx-2 cursor-pointer"
          onClick={sendData}
        >Confirmar</button>
      </div>
    </div>
  );
}
