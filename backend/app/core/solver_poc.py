import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy import select
from backend.app.core.database import SessionLocal
from backend.app.models.tms import PointDeVente, BaseLogistique

# --- ETAPE B : DISTANCE CALCULATION (Haversine) ---

def haversine(lat1, lon1, lat2, lon2):
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

def create_data_model():
    """Charge les données depuis la DB et prépare le modèle pour OR-Tools"""
    db = SessionLocal()
    data = {}
    
    # 1. Chargement Base Logistique (Dépôt)
    base = db.execute(select(BaseLogistique)).scalars().first()
    if not base:
        raise Exception("Aucune Base Logistique trouvée en DB. Lancez le seed !")

    # 2. Chargement PDV
    pdvs = db.execute(select(PointDeVente)).scalars().all()
    if not pdvs:
         raise Exception("Aucun PDV trouvé en DB. Lancez le seed !")

    # Liste ordonnée des Locations (Index 0 = Dépôt)
    locations = [(base.geo_lat, base.geo_lon)] + [(p.geo_lat, p.geo_lon) for p in pdvs]
    
    # Matrice de Distance
    print(f"Calcul de la matrice de distance pour {len(locations)} points...")
    distance_matrix = []
    for from_node in locations:
        row = []
        for to_node in locations:
            dist = haversine(from_node[0], from_node[1], to_node[0], to_node[1])
            row.append(dist)
        distance_matrix.append(row)
    
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = 5 # Fixé pour le POC
    data['depot'] = 0 # Index du dépôt dans locations
    
    data['names'] = [base.nom] + [p.nom for p in pdvs] # Pour l'affichage
    
    db.close()
    return data

def print_solution(data, manager, routing, solution):
    """Affiche la solution dans la console"""
    print(f"Objective: {solution.ObjectiveValue()} mètres")
    max_route_distance = 0
    total_distance = 0
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f"Route pour Véhicule {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            plan_output += f" {data['names'][node_index]} ->"
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        node_index = manager.IndexToNode(index) # Retour dépôt
        plan_output += f" {data['names'][node_index]}\n"
        plan_output += f"Distance de la route: {route_distance}m\n"
        print(plan_output)
        total_distance += route_distance

    print(f"Distance Totale de la flotte: {total_distance}m")

def main():
    # ETAPE A : Data Loading
    data = create_data_model()

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
        3000000,  # max distance par véhicule (ex: 3000km, très large pour ne pas bloquer)
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100) # Pour équilibrer les routes

    # ETAPE E : Solving
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10

    print("Recherche de solution en cours...")
    solution = routing.SolveWithParameters(search_parameters)

    # ETAPE F : Printing
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print('Pas de solution trouvée !')

if __name__ == '__main__':
    main()
