'use client';
import { AuthContext } from "@/components/providers/authProvider";
import { useContext } from "react";

export default function Home() {
  const { user } = useContext(AuthContext);
  return(
    <div>
      <h1 className="text-black text-3xl">Olá, {user?.username}</h1>
    </div>
  );
}