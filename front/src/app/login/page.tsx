'use client';
import { callGetCode } from "@/components/api/auth";
import { SnackbarContext } from "@/components/providers/snackbar";
import { useContext, useState } from "react";


export default function Login() {
    const { show } = useContext(SnackbarContext);
    const [cpf, setCpf] = useState("");
    const [phone, setPhone] = useState("");
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);

    async function getCode() {
        show("Enviando código", "Um código foi enviado para o seu telefone", "bg-dark-blue");
        await callGetCode(cpf, phone);
    }
    
    return(
        <div className="flex flex-col gap-4 justify-center items-center h-screen">
            <div className="max-w-[50%]">
                <img src="img//logo-blue.png" alt="Logo" />
            </div>
            <div className="flex flex-col gap-2">
                <input type="text" className="border-black border-2 rounded-lg text-black p-2" placeholder="CPF"/>
                <input type="text" className="border-black border-2 rounded-lg text-black p-2" placeholder="Telefone"/>
                <button className="bg-dark-blue rounded-lg p-3 text-lg font-inter" onClick={getCode}>Enviar código</button>
            </div>
        </div>
    );
}