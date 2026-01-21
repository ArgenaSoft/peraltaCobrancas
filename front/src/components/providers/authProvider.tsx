'use client';
import { createContext, useEffect, useMemo, useState } from "react";
import { callLogin, callAdminLogin, callRefresh, LoginReturn } from "../api/authApi";
import { useRouter, usePathname } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRightFromBracket, faArrowLeft, faHouse } from "@fortawesome/free-solid-svg-icons";
import { ApiResponse, UserTokens } from "../types";
import { registerRefreshHandler } from "../authTokenManager";


interface AuthContextType {
    user: UserTokens | null;
    ready: boolean;
    login: (cpf_cnpj: string, phone: string, code: string) => Promise<ApiResponse<LoginReturn>>;
    adminLogin: (cpf_cnpj: string, password: string) => Promise<ApiResponse<LoginReturn>>;
    refresh: () => Promise<string | null>;
}

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: any) => {
    const [isClient, setIsClient] = useState(false); // <- garante que está no client
    const [user, setUser] = useState<UserTokens | null>(null);
    const router = useRouter();
    const [ready, setReady] = useState<boolean>(false);

    // Carregamento inicial
    useEffect(() => {
        console.log("AuthProvider mounted");
        // Registra o handler de refresh para atualizar o token quando necessário
        registerRefreshHandler(refresh)
        // Verifica se o código está sendo executado no client
        setIsClient(true);
        console.log("Checking localStorage for tokens");
        const accessToken = localStorage.getItem("access_token");
        const refreshToken = localStorage.getItem("refresh_token");
        const username = localStorage.getItem("username");
        if (accessToken && refreshToken) {
            console.log("Found tokens in localStorage, setting user");
            setUser({
                access: accessToken,
                refresh: refreshToken,
                username: username ?? ""
            });
        }
        setReady(true);
    }, []);

    function updateTokenStorage(access: string | null = null, refresh: string | null = null, username: string | null = null) {
        if (access) {
            localStorage.setItem("access_token", access);
        }
        if (refresh) {
            localStorage.setItem("refresh_token", refresh);
        }
        if (username) {
            localStorage.setItem("username", username);
        }
    }

    async function login(cpf_cnpj: string, phone: string, code: string): Promise<ApiResponse<LoginReturn>> {
        let response: ApiResponse<LoginReturn> | ApiResponse = await callLogin(cpf_cnpj, phone, code);
        if (response.code == 200 && response.data) {
            setUser(response.data);
            updateTokenStorage(response.data.access, response.data.refresh, response.data.username);
        }
        return response;
    }

    async function adminLogin(cpf_cnpj: string, password: string): Promise<ApiResponse<LoginReturn>> {
        let response: ApiResponse<LoginReturn> | ApiResponse = await callAdminLogin(cpf_cnpj, password);
        if (response.code == 200 && response.data) {
            setUser(response.data);
            updateTokenStorage(response.data.access, response.data.refresh, response.data.username);
        }
        return response;
    }
    
    async function logout() {
        setUser(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("username");
        router.push('/login');
    }

    async function refresh(): Promise<string | null> {
        if (!user) {
            return null;
        }

        let data = await callRefresh(user.refresh);
        if (data) {
            setUser({
                ...user,
                access: data.data.access,
                refresh: data.data.refresh
            });
            updateTokenStorage(data.data.access, data.data.refresh);
            return data.data.access;
        }
        return null;
    }

    async function goHome() {
        if(!user) {
            router.push('/login');
            return;
        }
        if(user.username == "Administrador") {
            router.push('/admin');
        }else {
            router.push('/');
        }
    }

    return (
        <AuthContext.Provider value={useMemo(() => ({ login, adminLogin, refresh, user, ready }), [login, user])}>
            {isClient && user &&
                <div className="flex justify-between fixed top-0 left-0 w-full min-h-fit bg-dark-blue p-4">
                    <button
                        onClick={goHome}
                        className="text-white cursor-pointer"
                    >
                        <FontAwesomeIcon
                            size={"2x"}
                            icon={faHouse}
                        />
                    </button>

                    <button
                        onClick={logout}
                        className="text-white cursor-pointer"
                    >
                        <FontAwesomeIcon
                            size={"2x"}
                            icon={faArrowRightFromBracket}
                        />
                    </button>
                </div>

            }
            <div className={`h-screen ${isClient && user ? "pt-[120px] px-[40px]" : ""}`}>
                {children}
            </div>
        </AuthContext.Provider>
    );
}
