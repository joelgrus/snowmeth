import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { StoryCreateRequest, TaskResponse } from '../types';

// Query hooks
export function useStories() {
  return useQuery({
    queryKey: ['stories'],
    queryFn: () => apiClient.listStories(),
    staleTime: 30000, // 30 seconds
    refetchOnWindowFocus: false,
  });
}

export function useStory(storyId: string | null) {
  return useQuery({
    queryKey: ['story', storyId],
    queryFn: () => apiClient.getStory(storyId!),
    enabled: !!storyId,
    staleTime: 30000,
    refetchOnWindowFocus: false,
  });
}

// Mutation hooks
export function useCreateStory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: StoryCreateRequest) => apiClient.createStory(data),
    onSuccess: () => {
      // Invalidate stories list to refetch
      queryClient.invalidateQueries({ queryKey: ['stories'] });
    },
  });
}

export function useDeleteStory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (storyId: string) => apiClient.deleteStory(storyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stories'] });
    },
  });
}

export function useAdvanceStory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (storyId: string) => apiClient.advanceStory(storyId),
    onSuccess: (data, storyId) => {
      // Invalidate the specific story to refetch latest data
      queryClient.invalidateQueries({ queryKey: ['story', storyId] });
    },
  });
}

export function useRefineStory() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ storyId, instructions }: { storyId: string; instructions: string }) =>
      apiClient.refineStory(storyId, instructions),
    onSuccess: (data, { storyId }) => {
      queryClient.invalidateQueries({ queryKey: ['story', storyId] });
    },
  });
}

export function useAnalyzeStory() {
  return useMutation({
    mutationFn: (storyId: string) => apiClient.analyzeStory(storyId),
  });
}