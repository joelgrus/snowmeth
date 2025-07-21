// Clean types for the refactored app to avoid conflicts
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

export interface StepConfig {
  id: number;
  title: string;
  description: string;
  type: string;
  prerequisites?: number[];
}