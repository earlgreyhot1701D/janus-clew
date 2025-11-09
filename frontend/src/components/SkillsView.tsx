import { Code2 } from 'lucide-react';

interface Project {
  name: string;
  complexity_score: number;
  technologies: string[];
}

interface SkillsViewProps {
  projects: Project[];
}

export default function SkillsView({ projects }: SkillsViewProps) {
  // Extract unique skills with confidence and project mapping
  const skillsMap = new Map<string, { confidence: number; projects: string[] }>();

  projects.forEach((project) => {
    project.technologies.forEach((tech) => {
      if (!skillsMap.has(tech)) {
        skillsMap.set(tech, {
          confidence: 0.7 + (project.complexity_score / 20), // Confidence based on complexity
          projects: [],
        });
      }
      const skill = skillsMap.get(tech)!;
      skill.projects.push(project.name);
      skill.confidence = Math.min(1, skill.confidence + 0.1);
    });
  });

  const skills = Array.from(skillsMap.entries()).map(([name, data]) => ({
    name,
    ...data,
  }));

  const sortedSkills = skills.sort((a, b) => b.confidence - a.confidence);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Detected Skills
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
          Technologies and patterns identified across your projects
        </p>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sortedSkills.map((skill) => (
          <div
            key={skill.name}
            className="card p-6 hover:shadow-lg transition-shadow"
          >
            {/* Skill Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-teal-100 dark:bg-teal-900/30 rounded-lg">
                  <Code2 className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                </div>
                <h4 className="font-semibold text-slate-900 dark:text-white">
                  {skill.name}
                </h4>
              </div>
            </div>

            {/* Confidence Level */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <p className="text-xs text-slate-600 dark:text-slate-400">Confidence</p>
                <p className="text-xs font-medium text-teal-600 dark:text-teal-400">
                  {Math.round(skill.confidence * 100)}%
                </p>
              </div>
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-teal-500 to-teal-600 transition-all"
                  style={{ width: `${skill.confidence * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Projects Using This Skill */}
            <div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                Used in projects
              </p>
              <div className="flex flex-wrap gap-2">
                {skill.projects.map((project) => (
                  <span
                    key={project}
                    className="badge text-xs"
                  >
                    {project}
                  </span>
                ))}
              </div>
            </div>

            {/* Evidence Note */}
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                ✓ Detected from {skill.projects.length} project{skill.projects.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="card p-6 bg-gradient-to-br from-teal-50 to-teal-50/50 dark:from-teal-900/20 dark:to-teal-900/10">
        <h4 className="font-semibold text-slate-900 dark:text-white mb-3">
          Skills Summary
        </h4>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
              {skills.length}
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400">Unique Skills</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
              {projects.length}
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400">Projects</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
              {Math.round(
                (skills.reduce((sum, s) => sum + s.confidence, 0) / skills.length) * 100
              )}%
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400">Avg Confidence</p>
          </div>
        </div>
      </div>
    </div>
  );
}
