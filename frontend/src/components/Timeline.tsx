import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Project {
  name: string;
  complexity_score: number;
  commits: number;
  technologies: string[];
}

interface TimelineProps {
  projects: Project[];
}

export default function Timeline({ projects }: TimelineProps) {
  const data = projects.map((project, _index) => ({
    name: project.name,
    complexity: project.complexity_score,
    index: _index + 1,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Complexity Growth Timeline
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
          Track your code complexity progression across projects
        </p>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="name" 
              stroke="#94a3b8"
            />
            <YAxis 
              stroke="#94a3b8"
              domain={[0, 10]}
              label={{ value: 'Complexity Score', angle: -90, position: 'insideLeft' }}
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
            <Legend />
            <Line 
              type="monotone" 
              dataKey="complexity" 
              stroke="#14b8a6" 
              strokeWidth={3}
              dot={{ fill: '#14b8a6', r: 6 }}
              activeDot={{ r: 8 }}
              name="Complexity Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Project Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {projects.map((project) => (
          <div key={project.name} className="card p-6">
            <h4 className="font-semibold text-slate-900 dark:text-white mb-3">
              {project.name}
            </h4>
            
            <div className="space-y-3">
              <div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">Complexity</p>
                <div className="flex items-end gap-2">
                  <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
                    {project.complexity_score.toFixed(1)}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">/10</p>
                </div>
              </div>

              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-teal-500 to-teal-600"
                  style={{ width: `${(project.complexity_score / 10) * 100}%` }}
                ></div>
              </div>

              <div>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                  {project.commits} commits
                </p>
                <div className="flex flex-wrap gap-1">
                  {project.technologies.slice(0, 2).map((tech) => (
                    <span 
                      key={tech}
                      className="badge text-xs"
                    >
                      {tech}
                    </span>
                  ))}
                  {project.technologies.length > 2 && (
                    <span className="text-xs text-slate-600 dark:text-slate-400">
                      +{project.technologies.length - 2}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
