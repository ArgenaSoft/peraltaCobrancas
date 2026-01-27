'use client';
import { useContext, useState } from "react";
import { AuthContext } from "@/components/providers/authProvider";
import { FileInput } from "@/components/fileInput";
import { emitSnack } from "@/components/snackEmitter";
import { callSendFiles } from "@/components/api/spreadsheetApi";
import { useRouter } from "next/navigation";

export default function AdminPage() {
    const { user } = useContext(AuthContext);
    const [spreadsheet, setSpreadsheet] = useState<File | null>(null);
    const [boletos, setBoletos] = useState<File | null>(null);
    const router = useRouter();
    
    async function sendFiles() {
        if (!spreadsheet || !boletos) {
            emitSnack("Dados faltantes", "Selecione ambos os arquivos.","error");
            return;
        }

        let response = await callSendFiles(spreadsheet, boletos);
        if (response.code == 201) {
            emitSnack("Sucesso", "Planilha processada com sucesso.","info");
            router.push("admin/spreadsheet_results/" + response.data?.job_id);
        }else if(response.code == 200 && response.message) {
            emitSnack("", response.message, "info");
        } else {
            emitSnack("Erro", "Erro ao processar planilha.","error");
        }
    }

    return (
        <div>
            <div className="flex flex-col gap-4 items-center">
            <h1 className="text-black text-4xl mb-10">Olá, {user?.username}</h1>
                <div className="flex flex-col gap-4">
                    <div className="text-black flex gap-2 items-center">
                        <FileInput label="Selecionar planilha" name="spreadsheet" accept=".csv" callback={setSpreadsheet}/>
                        <FileInput label="Selecionar .zip com boletos" name="boletos" accept=".zip" callback={setBoletos}/>
                    </div>
                </div>

                <button 
                    className={`bg-dark-blue rounded-lg p-3 text-lg cursor-pointer`} 
                    type="submit"
                    onClick={sendFiles}
                >
                    Processar planilha
                </button>
            </div>
        </div>
    );
}