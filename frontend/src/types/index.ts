// Simple app types - clean slate for our refactored app
export interface Story {
  story_id: string;
  slug: string;
  story_idea: string;
  current_step: number;
  steps: Record<string, any>;
  created_at?: string;
}

export interface StoryCreateRequest {
  slug: string;
  story_idea: string;
}

export interface Character {
  name: string;
  description: string;
}

export interface GenerationEndpoint {
  url: string;
  buttonText: string;
  errorMessage: string;
}

export type StepNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

// Re-export API types for complex app (when needed)
export type { 
  TaskStatusResponse, 
  TaskResponse, 
  RefineRequest, 
  AnalysisResponse,
  CharacterChart,
  Scene,
  StepContent
} from './api';

// UI State types (for complex app)
export interface AppState {
  currentStoryId: string | null;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
}

export interface TasksState {
  activeTasks: Map<string, TaskStatusResponse>;
  taskHistory: TaskStatusResponse[];
}

// Step configuration
export interface StepConfig {
  id: number;
  title: string;
  description: string;
  type: 'text' | 'rich-text' | 'character-list' | 'character-charts' | 'scene-table' | 'scene-narratives';
  prerequisites?: number[];
}

// Editor props
export interface EditorProps<T = any> {
  content: T;
  onChange: (content: T) => void;
  onSave?: (content: T) => void;
  isLoading?: boolean;
  placeholder?: string;
}