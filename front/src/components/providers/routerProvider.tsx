'use client';
import { AuthContext } from "@/components/providers/authProvider";
import { usePathname, useRouter } from "next/navigation";
import { useContext, useEffect } from "react";

export default function RouterProvider({children,}: Readonly<{children: React.ReactNode;}>) {
  const {user, ready} = useContext(AuthContext);
  const router = useRouter();
  const pathname = usePathname();
  
  useEffect(() => {
    if(!ready) return;

    if(!user){
      console.log("No user, redirecting to login");
      if(pathname.includes('admin')){
        router.push("/admin/login");
      }else{
        router.push("/login");
      }
    }
  }, [ready, user, pathname]);

  if(!ready) {
    return <span className="text-black"> Carregando... </span>;
  }


  if(user || pathname.includes('login')) {
    return <>{children}</>;
  } else {
    return <span className="text-black">Erro no routing. Contate a administração e informe esta mensagem</span>;
  }

}