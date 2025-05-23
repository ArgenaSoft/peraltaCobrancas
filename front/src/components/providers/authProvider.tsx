'use client';
import { createContext, useEffect, useMemo, useState } from "react";
import { callLogin, callRefresh, LoginReturn } from "../api/authApi";
import { useRouter } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRightFromBracket } from "@fortawesome/free-solid-svg-icons";
import { ApiResponse } from "../api/types";
import { UserType } from "../types";


interface AuthContextType {
    user: UserType|null;
    login: (cpf: string, phone: string, code: string) => Promise<ApiResponse<LoginReturn>>;
}
export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: any) => {
    const [isClient, setIsClient] = useState(false); // <- garante que está no client
    const [user, setUser] = useState<UserType|null>(null);
    const router = useRouter();
    
    useEffect(() => {
        setIsClient(true);
        const accessToken = localStorage.getItem("access_token");
        const refreshToken = localStorage.getItem("refresh_token");
        const username = localStorage.getItem("username");
        if (accessToken && refreshToken) {
            setUser({
                access: accessToken,
                refresh: refreshToken,
                username: username ?? "",
            });
        }
    }, []);

    useEffect(() => {
        if (!isLogged()) {
            router.push('/login');
        }
    }, [user, router]);

    function updateTokenStorage(access: string|null = null, refresh: string|null = null, username: string|null = null){
        if(access){
            localStorage.setItem("access_token", access);
        }
        if(refresh){
            localStorage.setItem("refresh_token", refresh);
        }
        if(username){
            localStorage.setItem("username", username);
        }
    }

    // Função para verificar se o usuário está logado
    function isLogged(): boolean {
        return user !== null || localStorage.getItem("access_token") !== null;
    }

    async function login(cpf: string, phone: string, code: string): Promise<ApiResponse<LoginReturn>> {
        let response: ApiResponse<LoginReturn> | ApiResponse = await callLogin(cpf, phone, code);
        if(response.code == 200 && response.data){
            setUser(response.data);
            updateTokenStorage(response.data.access, response.data.refresh, response.data.username);
        }
        console.log(response);
        return response;
    }

    async function logout() {
        setUser(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("username");
        router.push('/login');
    }

    async function refresh(){
        if(!user){
            console.log("Não tem usuário para poder fazer refresh do token");
            return;
        }

        let data = await callRefresh(user.refresh);
        if(data){
            setUser({
                ...user,
                access: data.access,
                refresh: data.refresh
            });
            updateTokenStorage(data.access, data.refresh);
        }
    }

    return (
        <AuthContext.Provider value={useMemo(() => ({ login, user }), [login, user])}>
            {isClient && isLogged() && 
                <div className="flex justify-end fixed top-0 left-0 w-full h-[60px] bg-dark-blue p-3">
                    <FontAwesomeIcon icon={faArrowRightFromBracket} size={"2x"} onClick={logout}/>
                </div>
            }
            <div className={`h-screen ${isClient && isLogged() ? "pt-[120px] px-[40px]": ""}`}>
                {children}
            </div>
        </AuthContext.Provider>
    );
}
