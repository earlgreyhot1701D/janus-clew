import { Lightbulb, TrendingUp, CheckCircle, AlertCircle, Zap } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

interface Pattern {
  name: string;
  evidence: string | string[];
  impact: string;
  confidence: number;
  amazon_q_validated?: boolean;
  amazon_q_detected?: boolean;
  technologies?: string[];
}

interface Recommendation {
  title: string;
  description: string;
  status: 'ready' | 'not_ready' | 'explore';
  why: string;
  timeline?: string;
  technologies?: string[];
}

interface DevelopmentSignature {
  patterns?: Pattern[];
  preferences?: {
    description: string;
    traits?: string[];
  };
  trajectory?: {
    current_level: string;
    growth_velocity: string;
    next_milestone: string;
  };
  recommendations?: Recommendation[];
  amazon_q_technologies?: Record<string, number>;
  agentcore_insights?: {
    from_agentcore: boolean;
    model?: string;
    amazon_q_technologies_provided?: number;
    fallback_reason?: string;
    local_analysis_only?: boolean;
  };
  agentcore_available?: boolean;
}

export default function PatternsView() {
  const [signature, setSignature] = useState<DevelopmentSignature | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rawData, setRawData] = useState<any>(null); // For debugging

  useEffect(() => {
    loadSignature();
  }, []);

  const loadSignature = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getDevelopmentSignature();

      // Debug: log what we actually got
      console.log('Raw signature data:', data);
      setRawData(JSON.stringify(data, null, 2));

      setSignature(data || {});
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Failed to generate signature';
      console.error('Error loading signature:', err);
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-teal-200 dark:border-teal-900 border-t-teal-500 dark:border-t-teal-400 rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Analyzing your patterns...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-6">
        <p className="text-amber-700 dark:text-amber-300 font-semibold mb-4">
          Error: {error}
        </p>
        {rawData && (
          <details className="text-xs text-slate-600 dark:text-slate-400">
            <summary className="cursor-pointer font-semibold mb-2">Debug Info</summary>
            <pre className="bg-slate-100 dark:bg-slate-900 p-3 rounded overflow-auto max-h-64">
              {rawData}
            </pre>
          </details>
        )}
        <button
          onClick={loadSignature}
          className="mt-4 btn-secondary"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Safely extract data with fallbacks
  const amazonQTechList = signature?.amazon_q_technologies
    ? Object.entries(signature.amazon_q_technologies)
        .map(([tech, count]) => ({ tech, count }))
        .sort((a, b) => b.count - a.count)
    : [];

  const patterns = signature?.patterns || [];
  const recommendations = signature?.recommendations || [];
  const preferences = signature?.preferences || null;
  const trajectory = signature?.trajectory || null;
  const agentcoreAvailable = signature?.agentcore_available || false;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Your Development Signature
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Evidence-backed patterns, Amazon Q technologies, and intelligent recommendations
        </p>
      </div>

      {/* AgentCore Status - UPDATED MESSAGING */}
      <div className={`rounded-lg p-4 border ${
        agentcoreAvailable
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
          : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
      }`}>
        <div className="flex items-center gap-2">
          <Zap className={`w-5 h-5 ${
            agentcoreAvailable
              ? 'text-green-600 dark:text-green-400'
              : 'text-blue-600 dark:text-blue-400'
          }`} />
          <div>
            <p className={`font-semibold ${
              agentcoreAvailable
                ? 'text-green-700 dark:text-green-300'
                : 'text-blue-700 dark:text-blue-300'
            }`}>
              ✓ Evidence-Backed Analysis with AWS AgentCore
            </p>
            <p className={`text-sm ${
              agentcoreAvailable
                ? 'text-green-600 dark:text-green-400'
                : 'text-blue-600 dark:text-blue-400'
            }`}>
              Analyzes your repositories • Detects patterns • AWS AgentCore provides recommendations
            </p>
          </div>
        </div>
      </div>

      {/* Amazon Q Technologies */}
      {amazonQTechList.length > 0 && (
        <div className="card p-6 border-slate-200 dark:border-slate-800">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Technologies Detected by Amazon Q
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {amazonQTechList.map(({ tech, count }) => (
              <div
                key={tech}
                className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3"
              >
                <p className="font-medium text-slate-900 dark:text-white text-sm">{tech}</p>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  {count} project{count !== 1 ? 's' : ''}
                </p>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-4">
            💡 These technologies are factored into recommendations below
          </p>
        </div>
      )}

      {/* Trajectory Overview */}
      {trajectory && (
        <div className="card p-6 bg-gradient-to-br from-teal-50 to-teal-50/50 dark:from-teal-900/20 dark:to-teal-900/10 border-teal-200 dark:border-teal-800">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-teal-600 dark:text-teal-400" />
            Your Growth Trajectory
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Current Level</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {trajectory.current_level || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Growth Velocity</p>
              <p className="text-lg font-bold text-teal-600 dark:text-teal-400">
                {trajectory.growth_velocity || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Next Milestone</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {trajectory.next_milestone || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Detected Patterns */}
      {patterns.length > 0 ? (
        <div className="space-y-4">
          <h4 className="font-semibold text-slate-900 dark:text-white">
            Detected Patterns ({patterns.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.map((pattern, idx) => (
              <div key={pattern.name || idx} className="card p-6">
                <div className="flex items-start justify-between mb-3">
                  <h5 className="font-semibold text-slate-900 dark:text-white">
                    {pattern.name || 'Unknown Pattern'}
                  </h5>
                  <span className="text-xs font-medium bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 px-2 py-1 rounded">
                    {Math.round((pattern.confidence || 0) * 100)}% confidence
                  </span>
                </div>

                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                  {pattern.impact || 'No description'}
                </p>

                <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Evidence:</p>
                  <ul className="space-y-1">
                    {Array.isArray(pattern.evidence)
                      ? pattern.evidence.slice(0, 2).map((item, i) => (
                          <li key={i} className="text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2">
                            <span className="text-teal-600 dark:text-teal-400 mt-0.5">•</span>
                            <span>{String(item)}</span>
                          </li>
                        ))
                      : (
                          <li className="text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2">
                            <span className="text-teal-600 dark:text-teal-400 mt-0.5">•</span>
                            <span>{String(pattern.evidence)}</span>
                          </li>
                        )
                    }
                  </ul>
                </div>

                {pattern.technologies && pattern.technologies.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                    <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Related Technologies:</p>
                    <div className="flex flex-wrap gap-1">
                      {pattern.technologies.map((tech) => (
                        <span key={tech} className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-1 rounded">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card p-6 bg-slate-50 dark:bg-slate-900/20 border-slate-200 dark:border-slate-800">
          <p className="text-slate-600 dark:text-slate-400">No patterns detected yet. Analyze more projects to see patterns emerge.</p>
        </div>
      )}

      {/* Architectural Preferences */}
      {preferences ? (
        <div className="card p-6 border-slate-200 dark:border-slate-800">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4">
            Architectural Preferences
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            {preferences.description || 'No preference analysis available'}
          </p>
          {preferences.traits && preferences.traits.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {preferences.traits.map((trait) => (
                <span key={trait} className="inline-block bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full px-3 py-1 text-sm">
                  {trait}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 dark:text-slate-400">No traits identified yet</p>
          )}
        </div>
      ) : (
        <div className="card p-6 bg-slate-50 dark:bg-slate-900/20">
          <p className="text-slate-600 dark:text-slate-400 text-sm">Preference analysis not available</p>
        </div>
      )}

      {/* Intelligent Recommendations */}
      {recommendations.length > 0 ? (
        <div className="space-y-4">
          <h4 className="font-semibold text-slate-900 dark:text-white">
            Smart Recommendations{agentcoreAvailable && ' (from AWS AgentCore)'}
          </h4>
          <div className="grid grid-cols-1 gap-4">
            {recommendations.map((rec, index) => (
              <div
                key={`rec-${index}`}
                className={`card p-6 border-l-4 ${
                  rec.status === 'ready'
                    ? 'border-l-green-500 bg-green-50/50 dark:bg-green-900/10'
                    : rec.status === 'explore'
                      ? 'border-l-blue-500 bg-blue-50/50 dark:bg-blue-900/10'
                      : 'border-l-amber-500 bg-amber-50/50 dark:bg-amber-900/10'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3">
                    {rec.status === 'ready' && (
                      <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                    )}
                    {rec.status === 'explore' && (
                      <Lightbulb className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" />
                    )}
                    {rec.status === 'not_ready' && (
                      <AlertCircle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <h5 className="font-semibold text-slate-900 dark:text-white">
                        {rec.title || 'Recommendation'}
                      </h5>
                      <div className="mt-1 flex items-center gap-2">
                        <span className={`text-xs font-medium px-2 py-1 rounded ${
                          rec.status === 'ready'
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                            : rec.status === 'explore'
                              ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                              : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                        }`}>
                          {rec.status === 'ready'
                            ? '✓ Ready Now'
                            : rec.status === 'explore'
                              ? '💡 Consider'
                              : '⏸ Not Yet'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-slate-700 dark:text-slate-300 mb-3">
                  {rec.description || 'No description'}
                </p>

                {rec.why && (
                  <div className="bg-white/50 dark:bg-slate-800/50 rounded p-3 mb-3">
                    <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                      Why:
                    </p>
                    <p className="text-sm text-slate-700 dark:text-slate-300">
                      {rec.why}
                    </p>
                  </div>
                )}

                {rec.timeline && (
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    ⏱️ Timeline: {rec.timeline}
                  </p>
                )}

                {rec.technologies && rec.technologies.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {rec.technologies.map((tech) => (
                      <span key={tech} className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-1 rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card p-6 bg-slate-50 dark:bg-slate-900/20">
          <p className="text-slate-600 dark:text-slate-400 text-sm">No recommendations available yet</p>
        </div>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadSignature}
          className="btn-secondary"
        >
          Regenerate Signature
        </button>
      </div>
    </div>
  );
}
