// API Types - These should match the backend models

export interface Story {
  story_id: string;
  slug: string;
  story_idea: string;
  current_step: number;
  created_at?: string;
  steps: Record<string, any>;
}

export interface StoryCreateRequest {
  slug: string;
  story_idea: string;
}

export interface StoryResponse {
  story_id: string;
  slug: string;
  story_idea: string;
  current_step: number;
  created_at: string;
}

export interface StoryDetailResponse extends StoryResponse {
  steps: Record<string, any>;
}

export interface StoryListResponse {
  stories: StoryResponse[];
  total: number;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
}

export interface RefineRequest {
  instructions: string;
}

export interface AnalysisResponse {
  analysis: any;
}

// Character types for Step 3 and 7
export interface Character {
  name: string;
  description: string;
}

export interface CharacterChart {
  name: string;
  goal: string;
  motivation: string;
  conflict: string;
  epiphany: string;
  one_sentence_summary: string;
  one_paragraph_summary: string;
}

// Scene types for Step 8 and 9
export interface Scene {
  number: number;
  povCharacter: string;
  goal: string;
  conflict: string;
  outcome: string;
  narrative?: string;
}

// Step content types
export type StepContent = 
  | string  // Steps 1, 2, 4, 5, 6, 10
  | Character[]  // Step 3
  | CharacterChart[]  // Step 7
  | Scene[]  // Steps 8, 9
  | any;  // Fallback