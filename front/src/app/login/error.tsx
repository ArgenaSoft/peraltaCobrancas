'use client';
import { SnackbarContext } from "@/components/providers/snackbarProvider";
import { useContext, useEffect } from "react";

interface ErrorType {
    error: Error & { digest?: string };
    reset: () => void;
}

export default function Error({error, reset}: Readonly<ErrorType>) {
    const { show } = useContext(SnackbarContext);
    
    useEffect(() => {
        show("Erro", error.message, "error");    
    }, [error]);
    
    return(
        <div>
            <h1 className="text-4xl font-bold text-center">Erro</h1>
            <p className="text-center">{error.message}</p>
            <button onClick={() => reset()} className="bg-blue-500 text-white px-4 py-2 rounded">Tentar novamente</button>
        </div>
    );
}
