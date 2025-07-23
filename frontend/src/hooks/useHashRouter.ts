import { useState, useEffect, useCallback } from 'react';

interface Route {
  path: string;
  params: Record<string, string>;
}

export function useHashRouter() {
  const [currentRoute, setCurrentRoute] = useState<Route>(() => parseHash(window.location.hash));

  // Parse hash into route object
  function parseHash(hash: string): Route {
    const cleanHash = hash.slice(1) || '/'; // Remove # and default to /
    const parts = cleanHash.split('/').filter(p => p); // Filter out empty strings
    
    // Basic route matching for our app
    if (parts.length === 0 || parts[0] === 'stories') {
      if (parts.length === 2 && parts[1] === 'new') {
        return { path: 'stories-new', params: {} };
      }
      return { path: 'stories', params: {} };
    }
    
    if (parts[0] === 'story' && parts.length >= 2) {
      const storyId = parts[1];
      if (parts.length >= 4 && parts[2] === 'step') {
        const stepNum = parts[3];
        return { 
          path: 'story-step', 
          params: { storyId, step: stepNum } 
        };
      }
      return { path: 'story', params: { storyId } };
    }
    
    return { path: 'stories', params: {} };
  }

  // Navigate to a new route
  const navigate = useCallback((hash: string) => {
    window.location.hash = hash;
  }, []);

  // Handle hash change
  useEffect(() => {
    const handleHashChange = () => {
      setCurrentRoute(parseHash(window.location.hash));
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return {
    currentRoute,
    navigate,
  };
}