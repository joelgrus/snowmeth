import { useState, useEffect } from 'react';
import type { Story, StoryCreateRequest } from '../types/simple';

export const useStories = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStories = async () => {
    try {
      setError(null);
      const response = await fetch('/api/stories');
      if (!response.ok) throw new Error('Failed to fetch stories');
      const data = await response.json();
      setStories(data.stories);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLoading(false);
    }
  };

  const createStory = async (request: StoryCreateRequest): Promise<Story> => {
    const response = await fetch('/api/stories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to create story');
    }

    const newStory = await response.json();
    await fetchStories(); // Refresh list
    return newStory;
  };

  const deleteStory = async (storyId: string): Promise<void> => {
    const response = await fetch(`/api/stories/${storyId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Failed to delete story');
    }

    await fetchStories(); // Refresh list
  };

  const selectStory = async (story: Story): Promise<Story> => {
    const response = await fetch(`/api/stories/${story.story_id}`);
    if (!response.ok) throw new Error('Failed to fetch story details');
    return response.json();
  };

  const advanceStory = async (storyId: string): Promise<Story> => {
    const response = await fetch(`/api/stories/${storyId}/next`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to advance story');
    return response.json();
  };

  const rollbackStory = async (storyId: string, targetStep: number): Promise<Story> => {
    const response = await fetch(`/api/stories/${storyId}/rollback/${targetStep}`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to rollback story');
    return response.json();
  };

  useEffect(() => {
    fetchStories();
  }, []);

  return {
    stories,
    loading,
    error,
    fetchStories,
    createStory,
    deleteStory,
    selectStory,
    advanceStory,
    rollbackStory,
    setError
  };
};