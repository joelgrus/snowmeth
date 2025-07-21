import React, { useState } from 'react';
import { Story, StepNumber } from './types';
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
    setError
  } = useStories();

  const { generateContent, isGenerating } = useGeneration({
    onSuccess: (updatedStory) => {
      setSelectedStory(updatedStory);
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to advance story');
    }
  };

  const handleGenerate = async (stepNum: StepNumber) => {
    if (!selectedStory) return;
    await generateContent(selectedStory.story_id, stepNum);
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
              onAdvance={handleAdvanceStory}
              onGoToCurrent={() => setCurrentStep(selectedStory.current_step)}
              isGenerating={isGenerating}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;