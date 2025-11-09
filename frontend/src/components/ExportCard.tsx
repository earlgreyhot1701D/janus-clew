import { Download, Share2, Copy } from 'lucide-react';
import type { AnalysisData } from '../services/api';
import { useState } from 'react';

interface ExportCardProps {
  analysis: AnalysisData;
}

export default function ExportCard({ analysis }: ExportCardProps) {
  const [copied, setCopied] = useState(false);

  const generateHTML = () => {
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Growth Journey - Janus Clew</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8fafc;
            padding: 20px;
            color: #1e293b;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            padding: 40px;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #14b8a6;
            padding-bottom: 20px;
        }
        h1 { font-size: 2.5em; color: #0f766e; margin-bottom: 10px; }
        .subtitle { color: #64748b; font-size: 1.1em; }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .metric-card {
            background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value { font-size: 2em; font-weight: bold; }
        .metric-label { font-size: 0.9em; opacity: 0.9; margin-top: 5px; }
        .projects {
            margin-top: 40px;
        }
        .project {
            background: #f1f5f9;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #14b8a6;
        }
        .project-name { font-size: 1.3em; font-weight: bold; color: #0f766e; margin-bottom: 10px; }
        .project-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            font-size: 0.95em;
        }
        .detail { color: #475569; }
        .detail-label { font-weight: bold; color: #1e293b; }
        .badge {
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin: 2px;
        }
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #94a3b8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧵 My Growth Journey</h1>
            <p class="subtitle">Tracked with Janus Clew - Evidence-Backed Growth Tracking</p>
        </header>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">${analysis.overall.avg_complexity.toFixed(1)}</div>
                <div class="metric-label">Average Complexity /10</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${analysis.overall.growth_rate > 0 ? '+' : ''}${analysis.overall.growth_rate.toFixed(1)}%</div>
                <div class="metric-label">Growth Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${analysis.overall.total_projects}</div>
                <div class="metric-label">Projects Analyzed</div>
            </div>
        </div>

        <div class="projects">
            <h2 style="color: #0f766e; margin-bottom: 20px;">My Projects</h2>
            ${analysis.projects.map((p: any) => `
            <div class="project">
                <div class="project-name">${p.name}</div>
                <div class="project-details">
                    <div class="detail">
                        <div class="detail-label">Complexity</div>
                        <div>${p.complexity_score.toFixed(1)}/10</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Commits</div>
                        <div>${p.commits}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Technologies</div>
                        <div>
                            ${p.technologies.map((t: string) => `<span class="badge">${t}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
            `).join('')}
        </div>

        <footer>
            <p>Generated with Janus Clew v0.2.0</p>
            <p>Build your evidence-backed growth story at: https://github.com/yourusername/janus-clew</p>
        </footer>
    </div>
</body>
</html>`;
    return html;
  };

  const downloadHTML = () => {
    const html = generateHTML();
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `janus-clew-growth-${new Date().toISOString().split('T')[0]}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async () => {
    try {
      const html = generateHTML();
      await navigator.clipboard.writeText(html);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Share Your Growth
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
          Export your analysis as a shareable HTML card or download it for presentations
        </p>
      </div>

      {/* Export Preview */}
      <div className="card p-8 bg-gradient-to-br from-slate-50 to-slate-50/50 dark:from-slate-900 dark:to-slate-900/50">
        <div className="text-center space-y-6">
          <div>
            <div className="text-4xl font-bold text-teal-600 dark:text-teal-400 mb-2">
              {analysis.overall.avg_complexity.toFixed(1)}/10
            </div>
            <p className="text-slate-600 dark:text-slate-400">Average Complexity</p>
          </div>

          <div className="flex justify-center gap-8">
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {analysis.overall.growth_rate > 0 ? '+' : ''}{analysis.overall.growth_rate.toFixed(1)}%
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400">Growth</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {analysis.overall.total_projects}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400">Projects</p>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-2 pt-4 border-t border-slate-200 dark:border-slate-800">
            {analysis.projects.slice(0, 5).map((p) => (
              <span key={p.name} className="badge text-xs">
                {p.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={downloadHTML}
          className="card p-6 hover:shadow-lg transition-all cursor-pointer group"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-teal-100 dark:bg-teal-900/30 rounded-lg group-hover:bg-teal-200 dark:group-hover:bg-teal-900/50 transition-colors">
              <Download className="w-6 h-6 text-teal-600 dark:text-teal-400" />
            </div>
            <h4 className="font-semibold text-slate-900 dark:text-white">
              Download HTML
            </h4>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Export as a beautiful HTML file you can share or present
          </p>
        </button>

        <button
          onClick={copyToClipboard}
          className="card p-6 hover:shadow-lg transition-all cursor-pointer group"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-teal-100 dark:bg-teal-900/30 rounded-lg group-hover:bg-teal-200 dark:group-hover:bg-teal-900/50 transition-colors">
              <Copy className="w-6 h-6 text-teal-600 dark:text-teal-400" />
            </div>
            <h4 className="font-semibold text-slate-900 dark:text-white">
              {copied ? 'Copied!' : 'Copy HTML'}
            </h4>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Copy the HTML to clipboard for pasting into a blog or website
          </p>
        </button>
      </div>

      {/* Sharing Tips */}
      <div className="card p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <Share2 className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
              Sharing Tips
            </h4>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Share on LinkedIn to showcase your growth journey</li>
              <li>• Add to your portfolio or personal website</li>
              <li>• Include in presentations to potential employers</li>
              <li>• Track over time to visualize your learning progress</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
