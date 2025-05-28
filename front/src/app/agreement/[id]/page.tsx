'use client';
import { useParams } from "next/navigation";


export default function AgreementPage() {
    const { number } = useParams();

    return (
        <div className="flex flex-col gap-4 text-black justify-center items-center h-screen">
            <h1 className="text-4xl">Acordo {number}</h1>
            <span className="text-lg">Em breve...</span>
        </div>
    );

}