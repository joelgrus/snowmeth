import type { StepConfig, GenerationEndpoint, StepNumber } from '../types/simple';

export const SNOWFLAKE_STEPS: StepConfig[] = [
  {
    id: 1,
    title: 'One Sentence Summary',
    description: 'Summarize your story in one sentence',
    type: 'text',
  },
  {
    id: 2,
    title: 'One Paragraph Summary', 
    description: 'Expand your sentence into a paragraph',
    type: 'text',
    prerequisites: [1],
  },
  {
    id: 3,
    title: 'Characters',
    description: 'List your main characters',
    type: 'character-list',
    prerequisites: [1, 2],
  },
  {
    id: 4,
    title: 'Story Structure',
    description: 'Expand each plot point into a paragraph',
    type: 'rich-text',
    prerequisites: [1, 2, 3],
  },
  {
    id: 5,
    title: 'Character Synopses',
    description: 'Write a one-page synopsis for each character',
    type: 'rich-text',
    prerequisites: [1, 2, 3],
  },
  {
    id: 6,
    title: 'Detailed Story Synopsis',
    description: 'Expand your story structure into multiple pages',
    type: 'rich-text',
    prerequisites: [4],
  },
  {
    id: 7,
    title: 'Character Charts',
    description: 'Create detailed character development charts',
    type: 'character-charts',
    prerequisites: [3, 5],
  },
  {
    id: 8,
    title: 'Scene List',
    description: 'Create a spreadsheet of scenes',
    type: 'scene-table',
    prerequisites: [6],
  },
  {
    id: 9,
    title: 'Scene Narratives',
    description: 'Write narrative descriptions for each scene',
    type: 'scene-narratives',
    prerequisites: [8],
  },
  {
    id: 10,
    title: 'PDF Export',
    description: 'Export your complete story plan as PDF',
    type: 'pdf-export',
    prerequisites: [9],
  },
];

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
export const AUTO_SAVE_DELAY = parseInt(import.meta.env.VITE_AUTO_SAVE_DELAY || '2000');
export const TASK_TIMEOUT = parseInt(import.meta.env.VITE_TASK_TIMEOUT || '300000');

// Simple app constants
export const MAX_STEPS = 10;

export const STEP_TITLES: Record<StepNumber, string> = {
  1: 'One Sentence Summary',
  2: 'One Paragraph Summary', 
  3: 'Characters',
  4: 'Story Structure',
  5: 'Character Synopses',
  6: 'Detailed Story Synopsis',
  7: 'Character Charts',
  8: 'Scene List',
  9: 'Scene Expansions',
  10: 'PDF Export'
};

export const STEP_DESCRIPTIONS: Record<StepNumber, string> = {
  1: 'Summarize your story in one sentence',
  2: 'Expand your sentence into a paragraph',
  3: 'List your main characters',
  4: 'Expand each plot point into a paragraph',
  5: 'Write a one-page synopsis for each character',
  6: 'Expand your story structure into multiple pages',
  7: 'Create detailed character development charts',
  8: 'Create a spreadsheet of scenes',
  9: 'Expand each scene into a detailed mini-outline',
  10: 'Export your complete story plan as PDF'
};

export const GENERATION_ENDPOINTS: Record<StepNumber, GenerationEndpoint | null> = {
  1: {
    url: 'generate_initial_sentence',
    buttonText: '🔄 Regenerate Sentence',
    errorMessage: 'Failed to regenerate initial sentence'
  },
  2: {
    url: 'generate_paragraph_summary',
    buttonText: '✨ Generate Paragraph',
    errorMessage: 'Failed to generate paragraph summary'
  },
  3: {
    url: 'generate_characters', 
    buttonText: '✨ Generate Characters',
    errorMessage: 'Failed to generate characters'
  },
  4: {
    url: 'generate_plot_structure',
    buttonText: '✨ Generate Plot Structure', 
    errorMessage: 'Failed to generate plot structure'
  },
  5: {
    url: 'generate_character_synopses',
    buttonText: '✨ Generate Character Synopses',
    errorMessage: 'Failed to generate character synopses'
  },
  6: {
    url: 'generate_detailed_synopsis',
    buttonText: '✨ Generate Detailed Synopsis',
    errorMessage: 'Failed to generate detailed synopsis'
  },
  7: {
    url: 'generate_character_charts',
    buttonText: '✨ Generate Character Charts',
    errorMessage: 'Failed to generate character charts'
  },
  8: {
    url: 'generate_scene_breakdown',
    buttonText: '✨ Generate Scene List',
    errorMessage: 'Failed to generate scene breakdown'
  },
  9: {
    url: 'generate_scene_expansions',
    buttonText: '✨ Generate Scene Expansions',
    errorMessage: 'Failed to generate scene expansions'
  },
  10: null // No generation endpoint - PDF export component handles download
};

// Theme colors
export const COLORS = {
  primary: '#2196f3',
  success: '#28a745',
  warning: '#ffc107',
  danger: '#dc3545',
  secondary: '#6c757d',
  light: '#f8f9fa',
  border: '#ddd'
};

// Spacing
export const SPACING = {
  xs: '4px',
  sm: '8px', 
  md: '16px',
  lg: '24px',
  xl: '32px'
};