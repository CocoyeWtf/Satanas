import { useState } from 'react';
import { Truck, Map, Settings, Play, AlertCircle, Loader2 } from 'lucide-react';

// Import nommé explicite depuis le fichier API
import { runOptimization, type OptimizationResult } from './lib/api';

function App() {
  // Gestion d'état
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Action : Lancer l'optimisation
  const handleOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      // Appel API via notre fonction helper
      const data = await runOptimization();
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError("Impossible de contacter le serveur (Est-il lancé sur port 8000 ?)");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-50 font-sans">
      {/* Navbar */}
      <nav className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg">
            <Truck className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-300 bg-clip-text text-transparent">
            SATANAS TMS
          </h1>
        </div>
        <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
          <Settings className="h-5 w-5 text-slate-400" />
        </button>
      </nav>

      {/* Main Container */}
      <main className="flex-1 w-full max-w-5xl mx-auto p-6 space-y-8">

        {/* Hero Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 p-32 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="bg-slate-800 p-3 rounded-xl hidden md:block">
                <Map className="h-8 w-8 text-indigo-400" />
              </div>
              <div className="text-center md:text-left">
                <h2 className="text-2xl font-bold text-white mb-2">Optimisation de Tournées</h2>
                <p className="text-slate-400 max-w-lg">
                  Lancez le moteur de calcul pour générer les itinéraires optimaux pour la flotte active.
                </p>
              </div>
            </div>

            <button
              onClick={handleOptimization}
              disabled={loading}
              className={`
                flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white transition-all shadow-lg
                ${loading
                  ? 'bg-slate-700 cursor-wait opacity-80'
                  : 'bg-indigo-600 hover:bg-indigo-500 hover:scale-105 active:scale-95 shadow-indigo-900/20'}
              `}
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Play className="h-5 w-5 fill-current" />
              )}
              {loading ? 'Calcul en cours...' : 'Lancer le calcul'}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3 text-red-300">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Results List */}
        {result && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Résultats de l'optimisation
              </h3>
              <div className="text-sm font-mono text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full border border-emerald-400/20">
                Total: {(result.total_distance_meters / 1000).toFixed(1)} km
              </div>
            </div>

            <div className="grid gap-4">
              {result.routes.map((route, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/50 border border-slate-800 hover:border-indigo-500/30 rounded-xl p-5 transition-all"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                        <Truck className="h-6 w-6" />
                      </div>
                      <div>
                        <h4 className="font-medium text-white">Véhicule #{route.vehicle_id}</h4>
                        <p className="text-sm text-slate-500">{route.steps.length} étapes</p>
                      </div>
                    </div>
                    <span className="text-sm font-mono text-slate-400 bg-slate-950 px-2 py-1 rounded border border-slate-800">
                      {(route.distance_meters / 1000).toFixed(1)} km
                    </span>
                  </div>

                  {/* Steps Timeline */}
                  <div className="ml-5 pl-8 border-l border-slate-800 space-y-6 py-2 relative">
                    {route.steps.map((step, sIdx) => (
                      <div key={sIdx} className="relative">
                        <div className={`
                          absolute -left-[37px] h-4 w-4 rounded-full border-2 
                          ${step.stop_type === 'DEPOT'
                            ? 'bg-indigo-950 border-indigo-500'
                            : 'bg-slate-900 border-slate-600'}
                        `} />

                        <div className="flex justify-between items-center text-sm">
                          <span className={step.stop_type === 'DEPOT' ? 'text-indigo-300 font-medium' : 'text-slate-300'}>
                            {step.name}
                          </span>
                          {step.stop_type === 'DELIVERY' && (
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-500 uppercase tracking-wider">
                              Livraison
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
