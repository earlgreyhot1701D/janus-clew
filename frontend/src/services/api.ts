import axios from 'axios';
import type { AxiosInstance } from 'axios';

const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  const defaultUrl = 'http://localhost:3001/api';

  if (!envUrl || typeof envUrl !== 'string' || envUrl.trim() === '') {
    return defaultUrl;
  }

  try {
    new URL(envUrl);
    return envUrl;
  } catch {
    console.warn(`Invalid VITE_API_URL: ${envUrl}, using default`);
    return defaultUrl;
  }
};

const API_BASE_URL = getApiBaseUrl();

// Mock data for fallback
const MOCK_DATA = {
  analyses: [
    {
      timestamp: '2025-11-08_10-30-00',
      version: '0.2.0',
      projects: [
        {
          name: 'Your-Honor',
          path: '/home/user/Your-Honor',
          commits: 42,
          complexity_score: 6.2,
          technologies: ['AWS Bedrock', 'Python'],
          first_commit: '2025-09-15T08:00:00',
          q_analysis: {
            skill_level: 'intermediate',
            technologies: ['AWS Bedrock'],
          },
        },
        {
          name: 'Ariadne-Clew',
          path: '/home/user/Ariadne-Clew',
          commits: 78,
          complexity_score: 7.1,
          technologies: ['AWS Bedrock', 'AgentCore', 'Python'],
          first_commit: '2025-10-01T08:00:00',
          q_analysis: {
            skill_level: 'advanced',
            technologies: ['AWS Bedrock', 'AgentCore'],
          },
        },
        {
          name: 'TicketGlass',
          path: '/home/user/TicketGlass',
          commits: 125,
          complexity_score: 8.1,
          technologies: ['AWS Bedrock', 'AgentCore', 'FastAPI', 'Python'],
          first_commit: '2025-10-15T08:00:00',
          q_analysis: {
            skill_level: 'advanced',
            technologies: ['AWS Bedrock', 'AgentCore', 'FastAPI'],
          },
        },
      ],
      overall: {
        avg_complexity: 7.13,
        total_projects: 3,
        growth_rate: 30.6,
      },
      errors: [],
      patterns: null,
      recommendations: null,
    },
  ],
};

interface AnalysisData {
  timestamp: string;
  projects: any[];
  overall: {
    avg_complexity: number;
    total_projects: number;
    growth_rate: number;
  };
}

interface TimelinePoint {
  date: string;
  project_name: string;
  complexity: number;
  skills: string[];
}

interface Skill {
  name: string;
  confidence: number;
  projects: string[];
}

interface GrowthMetrics {
  avg_complexity: number;
  total_projects: number;
  growth_rate: number;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 5000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.warn('API error, falling back to mock data:', error.message);
        throw error;
      }
    );
  }

  async checkHealth(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch (error) {
      console.warn('API health check failed, using mock data');
      return false;
    }
  }

  async getAnalyses(): Promise<AnalysisData[]> {
    try {
      const response = await this.client.get<{ analyses: AnalysisData[] }>('/analyses');
      return response.data.analyses;
    } catch (error) {
      console.warn('Failed to fetch analyses, using mock data');
      return MOCK_DATA.analyses;
    }
  }

  async getLatestAnalysis(): Promise<AnalysisData> {
    try {
      const response = await this.client.get<{ analysis: AnalysisData }>('/analyses/latest');
      return response.data.analysis;
    } catch (error) {
      console.warn('Failed to fetch latest analysis, using mock data');
      return MOCK_DATA.analyses[0];
    }
  }

  async getTimeline(): Promise<TimelinePoint[]> {
    try {
      const response = await this.client.get<{ timeline: TimelinePoint[] }>('/timeline');
      return response.data.timeline;
    } catch (error) {
      console.warn('Failed to fetch timeline, using mock data');
      const analysis = MOCK_DATA.analyses[0];
      return analysis.projects.map((project) => ({
        date: analysis.timestamp,
        project_name: project.name,
        complexity: project.complexity_score,
        skills: project.technologies,
      }));
    }
  }

  async getSkills(): Promise<Skill[]> {
    try {
      const response = await this.client.get<{ skills: Skill[] }>('/skills');
      return response.data.skills;
    } catch (error) {
      console.warn('Failed to fetch skills, using mock data');
      const analysis = MOCK_DATA.analyses[0];
      const skillsMap: { [key: string]: Skill } = {};

      analysis.projects.forEach(project => {
        project.technologies.forEach((tech: string) => {
          if (!skillsMap[tech]) {
            skillsMap[tech] = {
              name: tech,
              confidence: 0.85,
              projects: [],
            };
          }
          skillsMap[tech].projects.push(project.name);
        });
      });

      return Object.values(skillsMap);
    }
  }

  async getGrowth(): Promise<GrowthMetrics> {
    try {
      const response = await this.client.get<{ metrics: GrowthMetrics }>('/growth');
      return response.data.metrics;
    } catch (error) {
      console.warn('Failed to fetch growth metrics, using mock data');
      return MOCK_DATA.analyses[0].overall;
    }
  }

  async getComplexityBreakdown(projectName: string): Promise<any> {
    try {
      const response = await this.client.get<{ breakdown: any }>(
        `/complexity/${projectName}`
      );
      return response.data.breakdown;
    } catch (error) {
      console.warn(`Failed to fetch complexity for ${projectName}, using mock data`);
      const project = MOCK_DATA.analyses[0].projects.find(
        p => p.name.toLowerCase() === projectName.toLowerCase()
      );
      if (project) {
        return {
          project: project.name,
          total_score: project.complexity_score,
          file_score: 3.0,
          function_score: 2.5,
          class_score: 1.2,
          nesting_score: 0.4,
          explanation: 'Multi-factor complexity analysis: files, functions, classes, and nesting',
        };
      }
      throw new Error(`Project ${projectName} not found`);
    }
  }

  async getDevelopmentSignature(): Promise<any> {
    try {
      const response = await this.client.get<{ status: string; signature: any }>(
        '/development-signature'
      );
      return response.data.signature;
    } catch (error) {
      console.warn('Failed to fetch development signature, using mock data');
      // Return mock development signature
      return {
        patterns: [
          {
            name: 'State Simplicity Preference',
            evidence: ['0/3 projects use databases'],
            confidence: 0.95,
            impact: 'Prefers simple state management over heavy database integration',
            amazon_q_validated: true,
          },
          {
            name: 'Async-First Architecture',
            evidence: ['2/3 projects use async patterns'],
            confidence: 0.88,
            impact: 'Builds with concurrency in mind from the start',
            amazon_q_validated: true,
          },
          {
            name: 'Rapid Learning Trajectory',
            evidence: ['Complexity grew from 6.2 to 8.1'],
            confidence: 0.92,
            impact: 'Shows accelerating technical growth',
            amazon_q_detected: false,
          },
          {
            name: 'Cloud-Native Development',
            evidence: ['Amazon Q detected AWS in 3 projects'],
            confidence: 0.95,
            impact: 'Comfortable building cloud-first architectures',
            amazon_q_detected: true,
            technologies: ['AWS', 'AWS Bedrock'],
          },
        ],
        preferences: {
          description:
            'You prefer building stateless, concurrent systems with cloud-first architecture. You avoid heavy database integration and favor async patterns.',
          traits: ['Stateless Design', 'Async-First', 'Cloud-Native', 'Concurrent Systems'],
        },
        trajectory: {
          current_level: 'Intermediate-Advanced',
          growth_velocity: '2.5x per project',
          next_milestone: 'Distributed Systems',
        },
        recommendations: [
          {
            title: 'Ready for Event-Driven Architecture',
            description: 'Your async-first approach combined with AWS usage makes you ready for event-driven systems.',
            status: 'ready',
            why: 'You use async patterns (confirmed by analysis) + AWS technologies (detected by Amazon Q in 3 projects)',
            timeline: 'Now',
            technologies: ['AWS EventBridge', 'SQS', 'SNS'],
          },
          {
            title: 'SQLite → PostgreSQL Path',
            description: 'When you need persistence, start with SQLite for simplicity, then graduate to PostgreSQL.',
            status: 'ready',
            why: 'Your stateless preference shows you prioritize simplicity. SQLite matches this philosophy before moving to PostgreSQL.',
            timeline: '2-3 weeks',
            technologies: ['SQLite', 'asyncpg', 'PostgreSQL'],
          },
          {
            title: 'Explore Advanced AWS Services',
            description: 'You\'re already using AWS Bedrock. Expand to Step Functions, AppSync, or EventBridge.',
            status: 'explore',
            why: 'Amazon Q detected Bedrock usage. You\'re ready for more sophisticated AWS patterns.',
            timeline: '3-4 weeks',
            technologies: ['Step Functions', 'AppSync', 'EventBridge'],
          },
        ],
        amazon_q_technologies: {
          Python: 3,
          'AWS Bedrock': 3,
          'AWS': 3,
          'async/await': 2,
          'AgentCore': 2,
          'FastAPI': 1,
        },
        agentcore_insights: {
          from_agentcore: false,
          local_analysis_only: true,
          amazon_q_technologies_provided: 6,
        },
        agentcore_available: false,
      };
    }
  }
}

export const apiClient = new APIClient();
export type { AnalysisData, TimelinePoint, Skill, GrowthMetrics };
