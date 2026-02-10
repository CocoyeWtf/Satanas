import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

// --- ON DÉFINIT L'INTERFACE ICI (Pour éviter l'erreur d'import) ---
interface Route {
    vehicle_id: number;
    steps: string[];
    distance: number;
}

interface RouteMapProps {
    routes: Route[];
}

// Correction des icônes Leaflet par défaut qui buggent souvent avec React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Composant pour recentrer la carte
function MapRecenter({ routes }: { routes: Route[] }) {
    const map = useMap();

    useEffect(() => {
        // Pour l'instant, on centre juste sur la France car on n'a pas encore les coordonnées précises
        // Quand on aura la géolocalisation, on utilisera map.fitBounds()
        map.setView([46.603354, 1.888334], 6);
    }, [routes, map]);

    return null;
}

export default function RouteMap({ routes }: RouteMapProps) {
    return (
        <div className="h-96 w-full rounded-lg overflow-hidden border border-slate-700 shadow-lg mb-8">
            <MapContainer center={[46.603354, 1.888334]} zoom={6} style={{ height: "100%", width: "100%" }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapRecenter routes={routes} />

                {/* Note: Pour l'instant la carte est "vide" de trajets car nous n'avons que des noms de villes.
            La prochaine étape (Géocodage) ajoutera les points. */}
            </MapContainer>
        </div>
    );
}