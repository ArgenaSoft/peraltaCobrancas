'use client';
import { AuthContext } from "@/components/providers/authProvider";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import TextInput from "@/components/textInput";
import { ApiResponse } from "@/components/types";
import { useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";


export default function LoginPage() {
  const router = useRouter();
  const { show } = useContext(SnackbarContext);
  const { adminLogin } = useContext(AuthContext);
  const [cpf_cnpj, setCpfCnpj] = useState("");
  const [password, setPassword] = useState("");
  const [disableSend, setDisableSend] = useState(false);

  useEffect(() => {
    if (password.length == 0 || cpf_cnpj.length < 14) {
      setDisableSend(true);
    } else {
      // Habilita o botão
      setDisableSend(false);
    }
  }, [password, cpf_cnpj]);

  async function handleClick() {

    let response: ApiResponse<LoginReturn> = await adminLogin(cpf_cnpj, password);
    if (response.code == 200) {
      show("Sucesso", "Login realizado com sucesso", "info");
      router.push("/admin");
    } else if(response.code == 401) {
      show("Erro", response.message ?? '', "error");
    }
  }

  return (
    <div className="flex flex-col gap-4 justify-center items-center h-screen">
      <div className="max-w-[70%]">
        <img src="/img/logo-blue.png" alt="Logo" />
      </div>
      <div className="flex flex-col items-center gap-2">
        {process.env.NEXT_PUBLIC_API_URL}
        <TextInput mask="___.___.___-__" replacement={{ _: /\d/ }} placeholder="CPF/CNPJ" value={cpf_cnpj} callback={setCpfCnpj} />
        <TextInput isPassword={true} placeholder="Senha" value={password} callback={setPassword} />

        <button className={`bg-dark-blue rounded-lg p-3 text-lg ${disableSend ? 'opacity-50' : ''} cursor-pointer`} onClick={handleClick} disabled={disableSend}>
          Entrar
        </button>
      </div>
    </div>
  );
}