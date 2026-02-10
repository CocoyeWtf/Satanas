import axios from "axios";

// --- INTERFACES ---
export interface Route {
    vehicle_id: number;
    steps: string[];
    distance: number;
}

export interface OptimizationResult {
    total_distance: number;
    routes: Route[];
}

// --- CONFIGURATION API ---
const api = axios.create({
    baseURL: "http://localhost:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
});

export const runOptimization = async (): Promise<OptimizationResult> => {
    try {
        const today = new Date().toISOString().split('T')[0];
        console.log(`[API] Envoi de la demande pour : ${today}`);

        // CORRECTION : Le backend exige "date_tournee"
        const response = await api.post("/optimize", {
            date_tournee: today
        });

        console.log("[API] Succès !", response.data);
        return response.data;

    } catch (error: any) {
        console.error("[API] Erreur :", error);
        // On garde l'alerte au cas où, mais ça devrait passer crème !
        if (axios.isAxiosError(error) && error.response) {
            alert(`Erreur Backend (${error.response.status}): \n` + JSON.stringify(error.response.data, null, 2));
        }
        throw error;
    }
};