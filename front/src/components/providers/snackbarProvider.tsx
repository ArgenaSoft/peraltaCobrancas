'use client';
import { createContext, useMemo, useState } from "react";

interface SnackbarContextType {
    show: (title?: string, message?: string, classes?: string) => void;
}

interface SnackType {
    title?: string;
    message?: string;
    classes?: string;
    callback?: (id: number) => void;
}

interface SnackbarProps extends SnackType {
    id: number;
}

const Snackbar = (props: SnackbarProps) => {
    const callback = props.callback ?? (() => {});

    return (
        <div className={`bg-dark-blue right-2 ${props.classes} rounded-lg p-5 flex flex-row justify-between items-center gap-5`} onClick={() => callback(props.id)}>
            <div className="flex flex-col">
                {props.title && <span className="font-bold text-[20px]">{props.title}</span>}
                {props.message && <span className="mt-1 text-[15px]">{props.message}</span>}
            </div>
        </div>
    );
}

export const SnackbarContext = createContext<SnackbarContextType>({} as SnackbarContextType);

export const SnackbarProvider = ({ children }: any) => {
    const [snacks, setSnacks] = useState<{[key: number]: SnackType}>({});
    const [snackCount, setSnackCount] = useState<number>(0);

    function show(title?: string, message?: string, classes?: string) {
        setSnackCount(prevCount => {
            console.log(prevCount)
            const id = prevCount;
    
            setSnacks(prev => ({
                ...prev,
                [id]: {
                    title,
                    message,
                    classes,
                    callback: remove
                }
            }));
    
            // remove após 4s
            setTimeout(() => {
                remove(id);
            }, 4000);
    
            return prevCount + 1;
        });
    }

    function remove(id: number) {
        console.log("Removendo snack " + id);
        setSnacks(prev => {
            const newSnacks = { ...prev };
            delete newSnacks[id];
            return newSnacks;
        });
    }

    return (
        <SnackbarContext.Provider value={useMemo(() => ({ show }), [show])}>
            <div className="flex flex-col fixed right-5 top-5 gap-2 z-10">
                {Object.keys(snacks).map(id => {
                    let snack: SnackType = snacks[parseInt(id)];
                    return <Snackbar key={id} id={parseInt(id)} title={snack.title} message={snack.message} classes={snack.classes} callback={remove} />
                })}
            </div>
            {children}
        </SnackbarContext.Provider>
    );
}

export type { SnackbarContextType };