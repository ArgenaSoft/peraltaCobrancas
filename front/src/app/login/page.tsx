'use client';
import { callGetCode, GetCodeReturn } from "@/components/api/authApi";
import { AuthContext } from "@/components/providers/authProvider";
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import TextInput from "@/components/textInput";
import { useRouter } from "next/navigation";
import { useContext, useState } from "react";


export default function Login() {
  const router = useRouter();
  const { show } = useContext(SnackbarContext);
  const { login } = useContext(AuthContext);
  const [cpf, setCpf] = useState("12345678901");
  const [phone, setPhone] = useState("12345678901");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);

  async function getCode() {
    let response: GetCodeReturn = await callGetCode(cpf, phone);
    console.log(response.code);
    show("Código enviado!", "Um código foi enviado para o seu telefone", "bg-dark-blue");
    setCodeSent(true);
  }

  async function handleClick(){
    if(codeSent){
      let succesful = await login(cpf, phone, code);
      if(succesful){
        show("Sucesso", "Login realizado com sucesso", "bg-dark-blue");
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
          <div className="max-w-[50%]">
              <img src="img//logo-blue.png" alt="Logo" />
          </div>
          <div className="flex flex-col gap-2 w-[75%]">
              {codeSent && 
                <span className="text-black text-[12px]">Um código foi enviado para o número { phone }</span>
              }
              <TextInput placeholder="CPF" value={cpf} callback={setCpf}/>
              <TextInput placeholder="Telefone" value={phone} callback={setPhone}/>

              {codeSent && 
                <TextInput placeholder="Código" value={code} callback={setCode}/>
              }
              <button className="bg-dark-blue rounded-lg p-3 text-lg" onClick={handleClick}>
                {codeSent ? "Entrar": "Enviar código"}
              </button>
          </div>
      </div>
  );
}