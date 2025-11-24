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
  patterns: Pattern[];
  preferences: {
    description: string;
    traits: string[];
  };
  trajectory: {
    current_level: string;
    growth_velocity: string;
    next_milestone: string;
  };
  recommendations: Recommendation[];
  amazon_q_technologies: Record<string, number>;
  agentcore_insights: {
    from_agentcore: boolean;
    model?: string;
    amazon_q_technologies_provided?: number;
    fallback_reason?: string;
    local_analysis_only?: boolean;
  };
  agentcore_available: boolean;
}

export default function PatternsView() {
  const [signature, setSignature] = useState<DevelopmentSignature | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSignature();
  }, []);

  const loadSignature = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getDevelopmentSignature();
      setSignature(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate signature');
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

  if (error || !signature) {
    return (
      <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-6">
        <p className="text-amber-700 dark:text-amber-300">
          {error || 'Unable to generate signature. Run analysis first.'}
        </p>
        <button
          onClick={loadSignature}
          className="mt-4 btn-secondary"
        >
          Try Again
        </button>
      </div>
    );
  }

  const amazonQTechList = Object.entries(signature.amazon_q_technologies || {})
    .map(([tech, count]) => ({ tech, count }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Your Development Signature
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Evidence-backed patterns, Amazon Q technologies, and intelligent recommendations from AWS AgentCore
        </p>
      </div>

      {/* AgentCore Status */}
      <div className={`rounded-lg p-4 border ${
        signature.agentcore_available
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
          : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
      }`}>
        <div className="flex items-center gap-2">
          <Zap className={`w-5 h-5 ${
            signature.agentcore_available
              ? 'text-green-600 dark:text-green-400'
              : 'text-blue-600 dark:text-blue-400'
          }`} />
          <div>
            <p className={`font-semibold ${
              signature.agentcore_available
                ? 'text-green-700 dark:text-green-300'
                : 'text-blue-700 dark:text-blue-300'
            }`}>
              {signature.agentcore_available
                ? '✓ AWS AgentCore Analysis Active'
                : '✓ Local Analysis (AgentCore Processing)'}
            </p>
            <p className={`text-sm ${
              signature.agentcore_available
                ? 'text-green-600 dark:text-green-400'
                : 'text-blue-600 dark:text-blue-400'
            }`}>
              {signature.agentcore_available
                ? signature.agentcore_insights.model || 'Bedrock AgentCore'
                : 'Using local analysis with graceful fallback'}
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
            💡 These technologies are factored into AgentCore recommendations below
          </p>
        </div>
      )}

      {/* Trajectory Overview */}
      {signature.trajectory && (
        <div className="card p-6 bg-gradient-to-br from-teal-50 to-teal-50/50 dark:from-teal-900/20 dark:to-teal-900/10 border-teal-200 dark:border-teal-800">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-teal-600 dark:text-teal-400" />
            Your Growth Trajectory
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Current Level</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {signature.trajectory.current_level}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Growth Velocity</p>
              <p className="text-lg font-bold text-teal-600 dark:text-teal-400">
                {signature.trajectory.growth_velocity}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Next Milestone</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {signature.trajectory.next_milestone}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Detected Patterns */}
      {signature.patterns && signature.patterns.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-slate-900 dark:text-white">
            Detected Patterns ({signature.patterns.length})
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {signature.patterns.map((pattern) => (
              <div key={pattern.name} className="card p-6">
                <div className="flex items-start justify-between mb-3">
                  <h5 className="font-semibold text-slate-900 dark:text-white">
                    {pattern.name}
                  </h5>
                  <div className="flex gap-2">
                    <span className="text-xs font-medium bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 px-2 py-1 rounded">
                      {Math.round(pattern.confidence * 100)}%
                    </span>
                    {pattern.amazon_q_validated && (
                      <span className="text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded">
                        ✓ Q Confirmed
                      </span>
                    )}
                    {pattern.amazon_q_detected && (
                      <span className="text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 px-2 py-1 rounded">
                        🔍 Q Detected
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                  {pattern.impact}
                </p>

                <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">Evidence:</p>
                  <ul className="space-y-1">
                    {Array.isArray(pattern.evidence)
                      ? pattern.evidence.slice(0, 2).map((item, i) => (
                          <li key={i} className="text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2">
                            <span className="text-teal-600 dark:text-teal-400 mt-0.5">•</span>
                            <span>{item}</span>
                          </li>
                        ))
                      : (
                          <li className="text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2">
                            <span className="text-teal-600 dark:text-teal-400 mt-0.5">•</span>
                            <span>{pattern.evidence}</span>
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
      )}

      {/* Architectural Preferences */}
      {signature.preferences && (
        <div className="card p-6 border-slate-200 dark:border-slate-800">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4">
            Architectural Preferences
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            {signature.preferences.description}
          </p>
          <div className="flex flex-wrap gap-2">
            {signature.preferences.traits.map((trait) => (
              <span key={trait} className="badge">
                {trait}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Intelligent Recommendations */}
      {signature.recommendations && signature.recommendations.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-slate-900 dark:text-white">
            Smart Recommendations{signature.agentcore_available && ' (from AWS AgentCore)'}
          </h4>
          <div className="grid grid-cols-1 gap-4">
            {signature.recommendations.map((rec, index) => (
              <div
                key={index}
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
                        {rec.title}
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
                  {rec.description}
                </p>

                <div className="bg-white/50 dark:bg-slate-800/50 rounded p-3 mb-3">
                  <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                    Why:
                  </p>
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    {rec.why}
                  </p>
                </div>

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
