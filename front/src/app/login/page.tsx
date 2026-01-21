'use client';
import { callGetCode, LoginReturn } from "@/components/api/authApi";
import { AuthContext } from "@/components/providers/authProvider";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import Switch from "@/components/switch";
import TextButton from "@/components/textButton";
import TextInput from "@/components/textInput";
import { ApiResponse } from "@/components/types";
import { useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";


export default function LoginPage() {
  const router = useRouter();
  const { show } = useContext(SnackbarContext);
  const { login } = useContext(AuthContext);
  const [cpf_cnpj, setCpfCnpj] = useState("");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [disableSend, setDisableSend] = useState(false);
  const [isCpf, setIsCpf] = useState(true);
  const cpfMask = "___.___.___-__";
  const cnpjMask = "__.___.___/____-__";

  useEffect(() => {
    if (phone.length < 11 || cpf_cnpj.length < 11) {
      setDisableSend(true);
    } else if (codeSent && code.length < 6) {
      setDisableSend(true);
    } else {
      // Habilita o botão
      setDisableSend(false);
    }
  }, [phone, cpf_cnpj, code, codeSent]);

  async function getCode() {
    let response: ApiResponse = await callGetCode(cpf_cnpj, phone);
    if(response.code == 201) {
      setCode(typeof response.data.code === "string" ? response.data.code : "");
      show("Código enviado!", "Um código foi enviado para o seu telefone", "info");
      setCodeSent(true);
    } else if (response.code == 500 && response.message === "Não foi possível enviar o SMS. Peça o código para o suporte.") {
      show("Erro", response.message ?? '', "error");
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

    let response: ApiResponse<LoginReturn> = await login(cpf_cnpj, phone, code);
    if (response.code == 200) {
      show("Sucesso", "Login realizado com sucesso", "info");
      router.push("/");
    } else if(response.code == 401) {
      show("Erro", response.message ?? '', "error");
    }
  }

  function changeDocumentType(value: boolean) {
    setIsCpf(value);
    setCpfCnpj("");
  }

  return (
    <div className="flex flex-col gap-4 justify-center items-center h-screen">
      <div className="max-w-[70%]">
        <img src="img//logo-blue.png" alt="Logo" />
      </div>
      <div className="flex flex-col items-center gap-2 w-75">
        {codeSent &&
          <span className="text-black text-[12px] text-center">Um código foi enviado para o número {phone}</span>
        }
        <div className="flex w-full items-center gap-1">
          <Switch state={isCpf} onValue="CPF" offValue="CNPJ" setState={changeDocumentType}/>
          <TextInput
            classes="flex-1 min-w-0"
            key={isCpf ? "cpf" : "cnpj"}
            mask={isCpf ? cpfMask : cnpjMask}
            replacement={{ _: /\d/ }}
            placeholder={isCpf ? "CPF" : "CNPJ"}
            value={cpf_cnpj}
            callback={setCpfCnpj}
          />
        </div>

        <TextInput classes="flex-1 min-w-0 w-full" mask="(__) _____-____" replacement={{ "_": /\d/ }} placeholder="Telefone" value={phone} callback={setPhone} />

        {codeSent &&
          <>
            <TextInput classes="flex-1 min-w-0" placeholder="Código" value={code} callback={setCode} />
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