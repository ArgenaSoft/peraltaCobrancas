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
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown, faChevronUp } from "@fortawesome/free-solid-svg-icons";
import Loader from "@/components/loader";

export default function SpreadsheetResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<SpreadsheetState | null>(null);
  const [showPayers, setShowPayers] = useState<boolean>(false);
  const [showCreditors, setShowCreditors] = useState<boolean>(false);
  const [sending, setSending] = useState<boolean>(false);
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
    setSending(true);

    const response = await callSaveSpreadsheetResults(id, denormalizeSpreadsheet(state));
    if (response.code != 200) {
      console.error("Error updating results:", response.message);
      emitSnack("Erro", response.message ?? "Erro ao salvar dados.","error");
      return;
    }

    router.push("/admin");
  }

  function switchShowPayers() {
    setShowPayers(!showPayers);
  }

  function switchShowCreditors() {
    setShowCreditors(!showCreditors);
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
    <div className="h-screen max-h-screen flex flex-col overflow-hidden">
      <div className="text-black flex flex-col items-center justify-center p-2 flex-1 min-h-0">
        <h1 className="text-[35px] flex-shrink-0 mb-4">Confirmar dados</h1>

        <div id="payers-list" className={`flex flex-col gap-4 items-center w-full transition-all duration-300 ease-in-out ${showPayers ? 'flex-1 min-h-0' : 'flex-shrink-0'}`}>
          <div className="flex items-center justify-between w-full self-start" onClick={switchShowPayers}>
            <h2 className="text-[25px] flex-shrink-0 bg-white z-10">Pagadores e acordos</h2>
            <FontAwesomeIcon
              icon={showPayers ? faChevronUp : faChevronDown}
              className="text-dark-blue text-[20px] cursor-pointer transition-transform duration-200 ease-in-out"
            />
          </div>
          {showPayers && (
            <div className="flex flex-col gap-4 overflow-y-auto scroll-smooth flex-1 w-full min-h-0 px-4 max-w-[90vw]">
              {payers.map((payer) => (
                <div key={payer.id} 
                  className={`rounded-2xl bg-dark-blue flex flex-col border-2 
                  border-dark-blue overflow-clip w-full max-w-[80vw] mx-auto flex-shrink-0`}>
                  <div className="flex justify-around items-center bg-white p-2">
                    <span className={`basis-2/3 text-[15px] ${payer.deleted ? "line-through opacity-20" : ""}`}>{payer.name}</span>

                    <DeleteRevertButton item={payer} 
                      onDelete={() => deletePayer(setState, payer.id)} 
                      onRevert={() => revertPayer(setState, payer.id)}
                      enabled={true}
                      />
                  </div>

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
          )}
        </div>

        <div id="creditors-list" className={`flex flex-col gap-4 items-center w-full transition-all duration-300 ease-in-out ${showCreditors ? 'flex-1 min-h-0' : 'flex-shrink-0'}`}>
          <div className="flex items-center justify-between w-full self-start" onClick={switchShowCreditors}>
            <h2 className="text-[25px] flex-shrink-0 bg-white z-10">Credores</h2>
            <FontAwesomeIcon
              icon={showCreditors ? faChevronUp : faChevronDown}
              className="text-dark-blue text-[20px] cursor-pointer transition-transform duration-200 ease-in-out"
            />
          </div>
          {showCreditors && (
            <div className="flex flex-col gap-4 overflow-y-auto scroll-smooth flex-1 w-full min-h-0 px-4 max-w-[90vw]">
              {Object.values(state.creditors).length > 0 && Object.values(state.creditors).map((creditor) => (
                <div key={creditor.id} className="flex p-2 border-b-2 border-black w-full justify-between">
                  <span className="text-[20px]">{creditor.name}</span>
                </div>
              ))
              }
            </div>
          )}
        </div>
      </div>
      <div id="buttons" className="fixed bottom-0 left-0 right-0 flex justify-between w-full rounded-t-2xl border-b-0 border-2 border-dark-blue bg-white shadow-2xl p-4 z-10">
        <button className="bg-white text-dark-blue border-2 border-dark-blue p-3 rounded-lg mx-2 cursor-pointer"
          onClick={()=>{router.push("/admin")}}
        >Cancelar</button>
        <button className={`bg-dark-blue text-white p-3 rounded-lg mx-2 cursor-pointer ${sending ? "opacity-50 cursor-not-allowed" : ""}`}
          onClick={sendData}
          disabled={sending}>
            {sending? <Loader /> : "Confirmar"}
        </button>
      </div>
    </div>
  );
}
