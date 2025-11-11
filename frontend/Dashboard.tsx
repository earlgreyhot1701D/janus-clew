import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Zap } from 'lucide-react';
import Timeline from '../components/Timeline';
import SkillsView from '../components/SkillsView';
import GrowthMetrics from '../components/GrowthMetrics';
import ExportCard from '../components/ExportCard';
import PatternsView from '../components/PatternsView';
import { apiClient, type AnalysisData } from '../services/api';

type TabType = 'timeline' | 'skills' | 'patterns' | 'export';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('timeline');
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const latestAnalysis = await apiClient.getLatestAnalysis();
      setAnalysis(latestAnalysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-teal-200 dark:border-teal-900 border-t-teal-500 dark:border-t-teal-400 rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-6">
        <p className="text-red-700 dark:text-red-300">
          {error || 'No analysis data available'}
        </p>
        <button
          onClick={loadData}
          className="mt-4 btn-secondary"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            Your Growth Journey
          </h2>
          <p className="text-slate-600 dark:text-slate-400">
            Track your coding progress across {analysis.overall.total_projects} projects
          </p>
        </div>

        {/* Growth Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-teal-100 dark:bg-teal-900/30 rounded-lg">
                <BarChart3 className="w-6 h-6 text-teal-600 dark:text-teal-400" />
              </div>
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400">Average Complexity</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {analysis.overall.avg_complexity.toFixed(1)}/10
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-teal-100 dark:bg-teal-900/30 rounded-lg">
                <TrendingUp className="w-6 h-6 text-teal-600 dark:text-teal-400" />
              </div>
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400">Growth Rate</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {analysis.overall.growth_rate > 0 ? '+' : ''}{analysis.overall.growth_rate.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-teal-100 dark:bg-teal-900/30 rounded-lg">
                <Zap className="w-6 h-6 text-teal-600 dark:text-teal-400" />
              </div>
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400">Total Projects</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {analysis.overall.total_projects}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-800">
        <div className="flex gap-8 overflow-x-auto">
          {['timeline', 'skills', 'patterns', 'export'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as TabType)}
              className={`py-4 px-2 font-medium border-b-2 transition-colors capitalize whitespace-nowrap ${
                activeTab === tab
                  ? 'border-teal-500 text-teal-600 dark:text-teal-400'
                  : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              {tab}
              {tab === 'patterns' && (
                <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300">
                  NEW
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'timeline' && <Timeline projects={analysis.projects} />}
        {activeTab === 'skills' && <SkillsView projects={analysis.projects} />}
        {activeTab === 'patterns' && <PatternsView />}
        {activeTab === 'export' && <ExportCard analysis={analysis} />}
      </div>

      {/* Growth Metrics */}
      <GrowthMetrics projects={analysis.projects} />

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadData}
          className="btn-secondary"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
}
