'use client';
import { callGetCode, GetCodeReturn } from "@/components/api/authApi";
import { AuthContext } from "@/components/providers/authProvider";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import TextInput from "@/components/textInput";
import { useRouter } from "next/navigation";
import { use, useContext, useEffect, useState } from "react";


export default function Login() {
  const router = useRouter();
  const { show } = useContext(SnackbarContext);
  const { login } = useContext(AuthContext);
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [disableSend, setDisableSend] = useState(false);

  useEffect(() => {
    if(phone.length < 14 || cpf.length < 14){
      setDisableSend(true);
    }else if(codeSent && code.length < 6){
      setDisableSend(true);
    }else{
      // Habilitar
      setDisableSend(false);
    }
  }, [phone, cpf, code, codeSent]);

  async function getCode() {
    let response: GetCodeReturn = await callGetCode(cpf, phone);
    show("Código enviado!", "Um código foi enviado para o seu telefone", "info");
    setCodeSent(true);
  }

  async function handleClick(){
    if(codeSent){
      let succesful = await login(cpf, phone, code);
      if(succesful){
        show("Sucesso", "Login realizado com sucesso", "info");
        router.push("/");
      }else{
        console.log("Erro ao fazer login");
      }
    }else{
      await getCode();
    }
  }

  return(
      <div className="flex flex-col gap-4 justify-center items-center h-screen">
          <div className="max-w-[70%]">
              <img src="img//logo-blue.png" alt="Logo" />
          </div>
          <div className="flex flex-col items-center gap-2">
              {codeSent && 
                <span className="text-black text-[12px]">Um código foi enviado para o número { phone }</span>
              }
              <TextInput mask="___.___.___-__" replacement={{ _: /\d/ }}  placeholder="CPF" value={cpf} callback={setCpf}/>
              <TextInput mask="(__) _____-____" replacement={{ "_": /\d/}} placeholder="Telefone" value={phone} callback={setPhone}/>

              {codeSent && 
                <TextInput placeholder="Código" value={code} callback={setCode}/>
              }
              <button className={`bg-dark-blue rounded-lg p-3 text-lg ${disableSend ? 'opacity-50': ''} cursor-pointer`} onClick={handleClick} disabled={disableSend}>
                {codeSent ? "Entrar": "Enviar código"}
              </button>
          </div>
      </div>
  );
}