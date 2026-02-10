import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.tms import PointDeVente, BaseLogistique
from typing import List, Dict, Any

class OptimizationService:
    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Calcule la distance en mètres entre deux points géographiques (Lat/Lon)
        en utilisant la formule de Haversine.
        """
        R = 6371000  # Rayon de la Terre en mètres
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return int(R * c) # Retourne un entier (mètres) pour OR-Tools

    def create_data_model(self, db: Session, vehicules_count: int):
        """Charge les données depuis la DB et prépare le modèle pour OR-Tools"""
        data = {}
        
        # 1. Chargement Base Logistique (Dépôt)
        base = db.execute(select(BaseLogistique)).scalars().first()
        if not base:
            raise Exception("Aucune Base Logistique trouvée en DB.")

        # 2. Chargement PDV
        pdvs = db.execute(select(PointDeVente)).scalars().all()
        if not pdvs:
             raise Exception("Aucun PDV trouvé en DB.")

        # Liste ordonnée des Locations (Index 0 = Dépôt)
        locations = [(base.geo_lat, base.geo_lon)] + [(p.geo_lat, p.geo_lon) for p in pdvs]
        
        # Matrice de Distance
        # print(f"Calcul de la matrice de distance pour {len(locations)} points...")
        distance_matrix = []
        for from_node in locations:
            row = []
            for to_node in locations:
                dist = self.haversine(from_node[0], from_node[1], to_node[0], to_node[1])
                row.append(dist)
            distance_matrix.append(row)
        
        data['distance_matrix'] = distance_matrix
        data['num_vehicles'] = vehicules_count
        data['depot'] = 0 # Index du dépôt dans locations
        
        data['names'] = [base.nom] + [p.nom for p in pdvs] # Pour l'affichage/retour
        data['ids'] = [str(base.id)] + [str(p.id) for p in pdvs] # IDs réels
        
        return data

    def format_solution(self, data, manager, routing, solution) -> Dict[str, Any]:
        """Formate la solution en JSON structuré"""
        result = {
            "status": "OPTIMAL", # Simplifié
            "total_distance_meters": solution.ObjectiveValue(),
            "routes": []
        }

        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = {
                "vehicle_id": vehicle_id, # TODO: Mapper avec vrais IDs véhicules
                "steps": [],
                "distance_meters": 0
            }
            
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                
                step_type = "DEPOT" if node_index == 0 else "DELIVERY"
                
                route["steps"].append({
                    "stop_type": step_type,
                    "name": data['names'][node_index],
                    "id": data['ids'][node_index]
                })

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
            # Retour dépôt
            node_index = manager.IndexToNode(index)
            route["steps"].append({
                "stop_type": "DEPOT",
                "name": data['names'][node_index],
                "id": data['ids'][node_index]
            })
            
            route["distance_meters"] = route_distance
            result["routes"].append(route)
            
        return result

    def solve_tour(self, db: Session, vehicules_count: int = 5) -> Dict[str, Any]:
        """Lance l'optimisation"""
        # ETAPE A : Data Loading
        data = self.create_data_model(db, vehicules_count)

        # ETAPE C : OR-Tools Setup
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        # Callback de distance
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Définir le coût de l'arc = distance
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # ETAPE D : Constraints (Distance Dimension)
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000000,  # max distance par véhicule
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # ETAPE E : Solving
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.seconds = 5 # Rapide pour l'API

        solution = routing.SolveWithParameters(search_parameters)

        # ETAPE F : Return Result
        if solution:
            return self.format_solution(data, manager, routing, solution)
        else:
            return {"status": "NO_SOLUTION", "message": "Impossible de trouver une solution avec les contraintes actuelles."}
