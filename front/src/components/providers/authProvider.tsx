'use client';
import { createContext, useEffect, useMemo, useState } from "react";
import { callLogin, callRefresh, LoginReturn } from "../api/authApi";
import { useRouter } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRightFromBracket, faArrowLeft, faHouse } from "@fortawesome/free-solid-svg-icons";
import { ApiResponse, UserTokens } from "../types";
import { registerRefreshHandler } from "../authTokenManager";


interface AuthContextType {
    user: UserTokens | null;
    login: (cpf: string, phone: string, code: string) => Promise<ApiResponse<LoginReturn>>;
    refresh: () => Promise<string | null>;
}
export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: any) => {
    const [isClient, setIsClient] = useState(false); // <- garante que está no client
    const [user, setUser] = useState<UserTokens | null>(null);
    const router = useRouter();

    // Carregamento inicial
    useEffect(() => {
        // Registra o handler de refresh para atualizar o token quando necessário
        registerRefreshHandler(refresh)
        // Verifica se o código está sendo executado no client
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

    // Verifica se o usuário está logado e redireciona para a página de login se não estiver
    useEffect(() => {
        if (!isLogged()) {
            router.push('/login');
        }
    }, [user, router]);

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

    // Função para verificar se o usuário está logado
    function isLogged(): boolean {
        return user !== null || localStorage.getItem("access_token") !== null;
    }

    async function login(cpf: string, phone: string, code: string): Promise<ApiResponse<LoginReturn>> {
        let response: ApiResponse<LoginReturn> | ApiResponse = await callLogin(cpf, phone, code);
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

    return (
        <AuthContext.Provider value={useMemo(() => ({ login, refresh, user }), [login, user])}>
            {isClient && isLogged() &&
                <div className="flex justify-between fixed top-0 left-0 w-full h-[60px] bg-dark-blue p-3">
                    <div className="cursor-pointer" onClick={() => router.push('/')}>
                        <FontAwesomeIcon icon={faHouse} size={"2x"} />
                    </div>
                    <div className="cursor-pointer" onClick={logout}>
                        <FontAwesomeIcon className="cursor-pointer self-end" icon={faArrowRightFromBracket} size={"2x"} onClick={logout} />
                    </div>
                </div>
            }
            <div className={`h-screen ${isClient && isLogged() ? "pt-[120px] px-[40px]" : ""}`}>
                {children}
            </div>
        </AuthContext.Provider>
    );
}
