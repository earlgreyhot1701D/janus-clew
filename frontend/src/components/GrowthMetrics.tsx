import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface Project {
  name: string;
  complexity_score: number;
  commits: number;
  technologies: string[];
}

interface GrowthMetricsProps {
  projects: Project[];
}

export default function GrowthMetrics({ projects }: GrowthMetricsProps) {
  const sortedProjects = [...projects].sort((a, b) => 
    a.complexity_score - b.complexity_score
  );

  const chartData = sortedProjects.map((p) => ({
    name: p.name,
    complexity: p.complexity_score,
  }));

  const firstComplexity = sortedProjects[0]?.complexity_score || 0;
  const lastComplexity = sortedProjects[sortedProjects.length - 1]?.complexity_score || 0;
  const growthRate = firstComplexity > 0 
    ? ((lastComplexity - firstComplexity) / firstComplexity) * 100 
    : 0;

  const avgCommits = Math.round(
    projects.reduce((sum, p) => sum + p.commits, 0) / projects.length
  );

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
        Growth Analysis
      </h3>

      {/* Growth Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Growth Rate */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-slate-600 dark:text-slate-400">
              Growth Rate
            </h4>
            {growthRate >= 0 ? (
              <ArrowUp className="w-5 h-5 text-green-500" />
            ) : (
              <ArrowDown className="w-5 h-5 text-red-500" />
            )}
          </div>
          <p className={`text-3xl font-bold ${
            growthRate >= 0 
              ? 'text-green-600 dark:text-green-400' 
              : 'text-red-600 dark:text-red-400'
          }`}>
            {growthRate > 0 ? '+' : ''}{growthRate.toFixed(1)}%
          </p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">
            From {firstComplexity.toFixed(1)} to {lastComplexity.toFixed(1)}
          </p>
        </div>

        {/* Total Commits */}
        <div className="card p-6">
          <h4 className="font-medium text-slate-600 dark:text-slate-400 mb-4">
            Total Commits
          </h4>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {projects.reduce((sum, p) => sum + p.commits, 0)}
          </p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">
            ~{avgCommits} commits per project
          </p>
        </div>

        {/* Highest Complexity */}
        <div className="card p-6">
          <h4 className="font-medium text-slate-600 dark:text-slate-400 mb-4">
            Highest Complexity
          </h4>
          <p className="text-3xl font-bold text-teal-600 dark:text-teal-400">
            {lastComplexity.toFixed(1)}
          </p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">
            {sortedProjects[sortedProjects.length - 1]?.name}
          </p>
        </div>

        {/* Projects Count */}
        <div className="card p-6">
          <h4 className="font-medium text-slate-600 dark:text-slate-400 mb-4">
            Total Projects
          </h4>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {projects.length}
          </p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">
            Analyzed projects
          </p>
        </div>
      </div>

      {/* Complexity Distribution Chart */}
      <div className="card p-6">
        <h4 className="font-semibold text-slate-900 dark:text-white mb-4">
          Complexity Distribution
        </h4>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis 
                stroke="#94a3b8"
                domain={[0, 10]}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#e2e8f0',
                }}
                formatter={(value: number) => [value.toFixed(1), 'Complexity']}
              />
              <Bar 
                dataKey="complexity" 
                fill="#14b8a6"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Project Details Table */}
      <div className="card overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 dark:bg-slate-800">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400">
                Project
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400">
                Complexity
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400">
                Commits
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400">
                Technologies
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {projects.map((project) => (
              <tr
                key={project.name}
                className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                <td className="px-6 py-4 font-medium text-slate-900 dark:text-white">
                  {project.name}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-teal-500 to-teal-600"
                        style={{ width: `${(project.complexity_score / 10) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                      {project.complexity_score.toFixed(1)}/10
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-600 dark:text-slate-400">
                  {project.commits}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {project.technologies.map((tech) => (
                      <span key={tech} className="badge text-xs">
                        {tech}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
