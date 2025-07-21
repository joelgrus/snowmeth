import { useState } from 'react';
import type { Story, StepNumber } from './types/simple';
import { useStories } from './hooks/useStories';
import { useGeneration } from './hooks/useGeneration';
import { StoryList } from './components/StoryList';
import { NewStoryForm } from './components/NewStoryForm';
import { StepNavigation } from './components/StepNavigation';
import { StepContent } from './components/StepContent';
import styles from './styles/components.module.css';

function App() {
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [showNewStoryForm, setShowNewStoryForm] = useState(false);
  const [loadingStory, setLoadingStory] = useState(false);

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
      setSelectedStory(updatedStory);
      // Update current step view if it changed (e.g., due to refinement clearing later steps)
      setCurrentStep(updatedStory.current_step);
    },
    onError: setError
  });

  const handleSelectStory = async (story: Story) => {
    setLoadingStory(true);
    setError(null);
    try {
      const fullStory = await selectStory(story);
      setSelectedStory(fullStory);
      setCurrentStep(fullStory.current_step);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load story');
    } finally {
      setLoadingStory(false);
    }
  };

  const handleCreateStory = async (request: { slug: string; story_idea: string }) => {
    try {
      const newStory = await createStory(request);
      setSelectedStory(newStory);
      setCurrentStep(1);
      setShowNewStoryForm(false);
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
      setCurrentStep(updatedStory.current_step);
      
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

  if (loading) return <div className={styles.loading}>Loading stories...</div>;
  if (loadingStory) return <div className={styles.loading}>Loading story details...</div>;

  return (
    <div className={styles.app}>
      <h1 className={styles.title}>Snowflake Method - Writing Assistant</h1>
      
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
              onClick={() => setSelectedStory(null)}
            >
              ← Back to Stories
            </button>
            <h2 className={styles.storyTitle}>{selectedStory.slug}</h2>
            <p className={styles.storyDescription}>{selectedStory.story_idea}</p>
          </div>

          <div className={styles.storyLayout}>
            <StepNavigation
              story={selectedStory}
              currentStep={currentStep}
              onStepChange={setCurrentStep}
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
              onGoToCurrent={() => setCurrentStep(selectedStory.current_step)}
              onNavigateToStep={setCurrentStep}
              isGenerating={isGenerating}
              isRefining={isRefining}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;