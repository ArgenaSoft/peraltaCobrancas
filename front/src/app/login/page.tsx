'use client';
import { callGetCode, LoginReturn } from "@/components/api/authApi";
import { AuthContext } from "@/components/providers/authProvider";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import TextButton from "@/components/textButton";
import TextInput from "@/components/textInput";
import { ApiResponse } from "@/components/types";
import { useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";


export default function LoginPage() {
  const router = useRouter();
  const { show } = useContext(SnackbarContext);
  const { login } = useContext(AuthContext);
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [disableSend, setDisableSend] = useState(false);

  useEffect(() => {
    if (phone.length < 14 || cpf.length < 14) {
      setDisableSend(true);
    } else if (codeSent && code.length < 6) {
      setDisableSend(true);
    } else {
      // Habilita o botão
      setDisableSend(false);
    }
  }, [phone, cpf, code, codeSent]);

  async function getCode() {
    let response: ApiResponse = await callGetCode(cpf, phone);
    if(response.code == 201) {
      setCode(typeof response.data.code === "string" ? response.data.code : "");
      show("Código enviado!", "Um código foi enviado para o seu telefone", "info");
      setCodeSent(true);
    } else {
      show("Erro", response.message ?? '', "error");
    }
  }

  async function handleClick() {
    if (!codeSent){
      await getCode();
      return;
    }

    let response: ApiResponse<LoginReturn> = await login(cpf, phone, code);
    if (response.code == 200) {
      show("Sucesso", "Login realizado com sucesso", "info");
      router.push("/");
    } else if(response.code == 401) {
      show("Erro", response.message ?? '', "error");
    }
  }

  return (
    <div className="flex flex-col gap-4 justify-center items-center h-screen">
      <div className="max-w-[70%]">
        <img src="img//logo-blue.png" alt="Logo" />
      </div>
      <div className="flex flex-col items-center gap-2">
        {codeSent &&
          <span className="text-black text-[12px] text-center">Um código foi enviado para o número {phone}</span>
        }
        <TextInput mask="___.___.___-__" replacement={{ _: /\d/ }} placeholder="CPF" value={cpf} callback={setCpf} />
        <TextInput mask="(__) _____-____" replacement={{ "_": /\d/ }} placeholder="Telefone" value={phone} callback={setPhone} />

        {codeSent &&
          <>
            <TextInput placeholder="Código" value={code} callback={setCode} />
            <TextButton text="Reenviar" callback={getCode} />
          </>
        }
        <button className={`bg-dark-blue rounded-lg p-3 text-lg ${disableSend ? 'opacity-50' : ''} cursor-pointer`} onClick={handleClick} disabled={disableSend}>
          {codeSent ? "Entrar" : "Enviar código"}
        </button>
      </div>
    </div>
  );
}