import { useState } from 'react';
import type { Story, StepNumber } from '../types/simple';
import { GENERATION_ENDPOINTS } from '../utils/constants';

interface UseGenerationOptions {
  onSuccess?: (updatedStory: Story) => void;
  onError?: (error: string) => void;
}

export const useGeneration = ({ onSuccess, onError }: UseGenerationOptions = {}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);

  const generateContent = async (storyId: string, stepNum: StepNumber) => {
    const endpoint = GENERATION_ENDPOINTS[stepNum];
    
    if (!endpoint) {
      // Step 10 is handled by the NovelWriterEditor component, not this hook
      if (stepNum !== 10) {
        onError?.(`Generation not yet implemented for Step ${stepNum}`);
      }
      return;
    }

    setIsGenerating(true);

    try {
      const response = await fetch(`/api/stories/${storyId}/${endpoint.url}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(endpoint.errorMessage);
      }

      const updatedStory = await response.json();
      onSuccess?.(updatedStory);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : endpoint.errorMessage;
      onError?.(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const refineContent = async (storyId: string, stepNumber: number, instructions: string) => {
    setIsRefining(true);

    try {
      const response = await fetch(`/api/stories/${storyId}/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          step_number: stepNumber,
          instructions: instructions,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to refine content');
      }

      const updatedStory = await response.json();
      onSuccess?.(updatedStory);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refine content';
      onError?.(errorMessage);
    } finally {
      setIsRefining(false);
    }
  };

  return {
    generateContent,
    refineContent,
    isGenerating,
    isRefining
  };
};