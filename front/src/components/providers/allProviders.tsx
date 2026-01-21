'use client';

import { AuthProvider } from "@/components/providers/authProvider";
import { SnackbarProvider } from "@/components/providers/snackbarProvider";
import RouterProvider from "./routerProvider";

export function AllProviders({ children }: { children: React.ReactNode }) {
  return (
    <SnackbarProvider>
      <AuthProvider>
        <RouterProvider>
            {children}
        </RouterProvider>
      </AuthProvider>
    </SnackbarProvider>
  );
}
