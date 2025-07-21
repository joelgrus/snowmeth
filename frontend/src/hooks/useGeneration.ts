import { useState } from 'react';
import type { Story, StepNumber } from '../types/simple';
import { GENERATION_ENDPOINTS } from '../utils/constants';

interface UseGenerationOptions {
  onSuccess?: (updatedStory: Story) => void;
  onError?: (error: string) => void;
}

export const useGeneration = ({ onSuccess, onError }: UseGenerationOptions = {}) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const generateContent = async (storyId: string, stepNum: StepNumber) => {
    const endpoint = GENERATION_ENDPOINTS[stepNum];
    
    if (!endpoint) {
      onError?.(`Generation not yet implemented for Step ${stepNum}`);
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

  return {
    generateContent,
    isGenerating
  };
};