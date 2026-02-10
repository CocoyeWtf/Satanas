import axios from 'axios';

// 1. Configuration Axios
export const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// 2. Interfaces TypeScript (Corregido)
export interface Step {
    stop_type: 'DEPOT' | 'DELIVERY';
    name: string;
    id: string;
}

export interface Route {
    vehicle_id: number;
    steps: Step[];
    distance_meters: number;
}

export interface OptimizationResult {
    status: string;
    total_distance_meters: number;
    routes: Route[];
}

// 3. Fonctions API
export const runOptimization = async (): Promise<OptimizationResult> => {
    const today = new Date().toISOString().split('T')[0];

    // Appel POST vers /optimize
    const { data } = await api.post<OptimizationResult>('/optimize', {
        date_tournee: today,
        vehicle_ids: [] // IDs vides = Tous les véhicules
    });

    return data;
};
