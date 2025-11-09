import { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import { apiClient } from './services/api';

function App() {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const stored = localStorage.getItem('darkMode');
    return stored ? JSON.parse(stored) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [apiAvailable, setApiAvailable] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Persist dark mode preference
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    // Check API availability
    apiClient.checkHealth().then(setApiAvailable).finally(() => setLoading(false));
  }, []);

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-white dark:bg-slate-950 transition-colors duration-200">
        {/* Navigation */}
        <nav className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">J</span>
                </div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  Janus Clew
                </h1>
              </div>

              <div className="flex items-center gap-4">
                {!apiAvailable && (
                  <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-3 py-1 rounded-full">
                    Using demo data
                  </div>
                )}
                
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                  aria-label="Toggle dark mode"
                >
                  {darkMode ? (
                    <Sun className="w-5 h-5 text-amber-500" />
                  ) : (
                    <Moon className="w-5 h-5 text-slate-600" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="animate-spin w-12 h-12 border-4 border-teal-200 dark:border-teal-900 border-t-teal-500 dark:border-t-teal-400 rounded-full mx-auto mb-4"></div>
                <p className="text-slate-600 dark:text-slate-400">Loading...</p>
              </div>
            </div>
          ) : (
            <Dashboard />
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 py-8 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center text-sm text-slate-600 dark:text-slate-400">
              <p>🧵 Janus Clew v0.2.0 - Evidence-backed coding growth tracking</p>
              <p className="mt-2">Built for AWS Global Vibe: AI Coding Hackathon 2025</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
