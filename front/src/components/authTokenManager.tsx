// authTokenManager.ts
let refreshFn: (() => Promise<string|null>) | null = null;

export function registerRefreshHandler(fn: () => Promise<string|null>) {
  refreshFn = fn;
}

export async function tryRefreshToken(): Promise<string|null> {
    if (!refreshFn) {
        console.error("Refresh function not registered.");
        return null;
    }
    
    return await refreshFn();
}