import { Truck, Map, Settings } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Truck className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            SATANAS TMS
          </h1>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <Settings className="h-5 w-5 text-slate-400" />
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400">
        <div className="bg-slate-900 border border-slate-800 p-12 rounded-2xl max-w-lg w-full flex flex-col items-center gap-6 shadow-2xl">
          <div className="bg-slate-800 p-4 rounded-full">
            <Map className="h-12 w-12 text-blue-500" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold text-white">Système Prêt</h2>
            <p className="text-slate-400">
              Le moteur d'optimisation est en attente d'ordres.
              <br />
              Connecté à l'API <span className="text-green-400 font-mono text-sm bg-green-400/10 px-2 py-0.5 rounded">v1</span>
            </p>
          </div>
          <button className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-2.5 rounded-lg transition-all active:scale-95 w-full">
            Lancer une Optimisation
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
