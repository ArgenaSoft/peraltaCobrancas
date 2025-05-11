interface AuthContextType {
    user: UserType|null;
    login: (cpf: string, phone: string, code: string) => Promise<boolean>;
}

interface UserType {
    access: string;
    refresh: string;
    username: string;
};

export type { AuthContextType, UserType };