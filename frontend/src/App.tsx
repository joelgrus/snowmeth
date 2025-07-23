import { useState, useEffect } from 'react';
import type { Story, StepNumber } from './types/simple';
import { useStories } from './hooks/useStories';
import { useGeneration } from './hooks/useGeneration';
import { useHashRouter } from './hooks/useHashRouter';
import { StoryList } from './components/StoryList';
import { NewStoryForm } from './components/NewStoryForm';
import { StepNavigation } from './components/StepNavigation';
import { StepContent } from './components/StepContent';
import styles from './styles/components.module.css';

function App() {
  const { currentRoute, navigate } = useHashRouter();
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [showNewStoryForm, setShowNewStoryForm] = useState(false);
  const [loadingStory, setLoadingStory] = useState(false);
  const [navigationCollapsed, setNavigationCollapsed] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  const {
    stories,
    loading,
    error,
    createStory,
    deleteStory,
    selectStory,
    advanceStory,
    rollbackStory,
    setError
  } = useStories();

  const { generateContent, refineContent, isGenerating, isRefining } = useGeneration({
    onSuccess: (updatedStory) => {
      // Merge the incoming story data with the existing state to preserve local changes
      setSelectedStory(prevStory => ({ ...prevStory, ...updatedStory }));
      setCurrentStep(updatedStory.current_step);
    },
    onError: setError
  });

  // Handle route changes
  useEffect(() => {
    const loadFromRoute = async () => {
      if (currentRoute.path === 'story' || currentRoute.path === 'story-step') {
        const storyId = currentRoute.params.storyId;
        const step = currentRoute.params.step ? parseInt(currentRoute.params.step) : null;
        
        // Only load if we don't have this story selected
        if (!selectedStory || selectedStory.story_id !== storyId) {
          const story = stories.find(s => s.story_id === storyId);
          
          if (story) {
            setLoadingStory(true);
            setError(null);
            try {
              const fullStory = await selectStory(story);
              setSelectedStory(fullStory);
              setCurrentStep(step || fullStory.current_step);
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Failed to load story');
              navigate('#/stories');
            } finally {
              setLoadingStory(false);
            }
          }
        } else if (step && step !== currentStep) {
          // Just update step if story is already loaded
          setCurrentStep(step);
        }
      } else {
        // On stories route, clear selection
        setSelectedStory(null);
      }
    };

    if (stories.length > 0 || initialLoad) {
      loadFromRoute();
      if (initialLoad) {
        setInitialLoad(false);
      }
    }
  }, [currentRoute, stories, selectedStory, currentStep, selectStory, setError, navigate, initialLoad]);

  // Debounced effect for saving writing style
  useEffect(() => {
    if (!selectedStory || selectedStory.writing_style === undefined) {
      return;
    }

    const handler = setTimeout(async () => {
      try {
        await fetch(`/api/stories/${selectedStory.story_id}/writing_style`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ writing_style: selectedStory.writing_style }),
        });
      } catch (err) {
        console.error('Failed to save writing style:', err);
      }
    }, 1000); // Save 1 second after user stops typing

    return () => {
      clearTimeout(handler);
    };
  }, [selectedStory?.writing_style, selectedStory?.story_id]);


  // Scroll to step content when step changes
  const handleStepChange = (stepNum: number) => {
    setCurrentStep(stepNum);
    // Update URL when step changes - use callback to ensure we have the latest selectedStory
    setSelectedStory(story => {
      if (story) {
        navigate(`#/story/${story.story_id}/step/${stepNum}`);
      }
      return story;
    });
    // Small delay to ensure content is rendered
    setTimeout(() => {
      // Find the step header and scroll to it
      const stepHeader = document.querySelector('[class*="stepHeader"]');
      if (stepHeader) {
        stepHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        // Fallback to scrolling to top if header not found
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 100);
  };

  const handleSelectStory = async (story: Story) => {
    // Just navigate - let the route handler do the loading
    navigate(`#/story/${story.story_id}/step/${story.current_step}`);
  };

  const handleCreateStory = async (request: { slug: string; story_idea: string }) => {
    try {
      const newStory = await createStory(request);
      setSelectedStory(newStory);
      setCurrentStep(1);
      setShowNewStoryForm(false);
      // Navigate to the new story
      navigate(`#/story/${newStory.story_id}/step/1`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create story');
    }
  };

  const handleDeleteStory = async (storyId: string) => {
    try {
      await deleteStory(storyId);
      if (selectedStory && selectedStory.story_id === storyId) {
        setSelectedStory(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete story');
    }
  };

  const handleAdvanceStory = async () => {
    if (!selectedStory) return;
    
    try {
      const updatedStory = await advanceStory(selectedStory.story_id);
      setSelectedStory(updatedStory);
      handleStepChange(updatedStory.current_step);
      
      // Automatically trigger generation for the new current step
      await handleGenerate(updatedStory.current_step as StepNumber);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to advance story');
    }
  };

  const handleGenerate = async (stepNum: StepNumber) => {
    if (!selectedStory) return;
    await generateContent(selectedStory.story_id, stepNum);
  };

  const handleRefine = async (stepNumber: number, instructions: string) => {
    if (!selectedStory) return;
    await refineContent(selectedStory.story_id, stepNumber, instructions);
  };

  const handleImproveScene = async (sceneNumber: number, instructions: string) => {
    if (!selectedStory) return;
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/improve_scene`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scene_number: sceneNumber,
          improvement_instructions: instructions
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to improve scene');
      }
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to improve scene');
      throw err; // Re-throw so the component can handle loading states
    }
  };

  const handleRollback = async (targetStep: number) => {
    if (!selectedStory) return;
    
    try {
      const updatedStory = await rollbackStory(selectedStory.story_id, targetStep);
      setSelectedStory(updatedStory);
      setCurrentStep(updatedStory.current_step);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rollback story');
    }
  };

  const handleWritingStyleChange = (newStyle: string) => {
    if (selectedStory) {
      setSelectedStory({
        ...selectedStory,
        writing_style: newStyle,
      });
    }
  };

  if (loading) return <div className={styles.loading}>Loading stories...</div>;
  if (loadingStory) return <div className={styles.loading}>Loading story details...</div>;

  return (
    <div className={styles.app}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <a href="#/stories" style={{ textDecoration: 'none', color: 'inherit' }}>
            snowmeth - AI Novel-Writing Assistant
          </a>
        </h1>
        <img src="/snowmeth.png" alt="snowmeth logo" className={styles.logo} />
      </div>
      
      {error && (
        <div className={styles.error}>
          {error}
          <button 
            className={styles.errorCloseButton}
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}
      
      {!selectedStory ? (
        <div>
          {showNewStoryForm && (
            <NewStoryForm
              onSubmit={handleCreateStory}
              onCancel={() => {
                setShowNewStoryForm(false);
              }}
              isSubmitting={isGenerating}
            />
          )}

          <StoryList
            stories={stories}
            onSelectStory={handleSelectStory}
            onDeleteStory={handleDeleteStory}
            onNewStory={() => setShowNewStoryForm(true)}
            isDeleting={isGenerating}
          />
        </div>
      ) : (
        <div>
          <div className={styles.storyHeader}>
            <button
              className={styles.backButton}
              onClick={() => navigate('#/stories')}
            >
              ← Back to Stories
            </button>
            <h2 className={styles.storyTitle}>{selectedStory.slug}</h2>
            <p className={styles.storyDescription}>{selectedStory.story_idea}</p>
          </div>

          <div className={`${styles.storyLayout} ${navigationCollapsed ? styles.navigationCollapsed : ''}`}>
            <StepNavigation
              story={selectedStory}
              currentStep={currentStep}
              onStepChange={handleStepChange}
              collapsed={navigationCollapsed}
              onToggleCollapse={() => setNavigationCollapsed(!navigationCollapsed)}
            />

            <StepContent
              story={selectedStory}
              stepNum={currentStep as StepNumber}
              currentStep={currentStep}
              onGenerate={handleGenerate}
              onRefine={handleRefine}
              onImproveScene={handleImproveScene}
              onAdvance={handleAdvanceStory}
              onRollback={handleRollback}
              onGoToCurrent={() => handleStepChange(selectedStory.current_step)}
              onNavigateToStep={handleStepChange}
              onStoryUpdate={setSelectedStory}
              writingStyle={selectedStory.writing_style || ''}
              onWritingStyleChange={handleWritingStyleChange}
              isGenerating={isGenerating}
              isRefining={isRefining}
            />
          </div>
        </div>
      )}
      
      <footer className={styles.footer}>
        <p>
          Based on the{' '}
          <a 
            href="https://www.advancedfictionwriting.com/articles/snowflake-method/" 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.link}
          >
            Snowflake Method
          </a>{' '}
          by Randy Ingermanson · Built by{' '}
          <a 
            href="https://twitter.com/joelgrus" 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.link}
          >
            Joel Grus
          </a>
          {' · '}
          <a 
            href="https://github.com/joelgrus/snowmeth" 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.link}
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
