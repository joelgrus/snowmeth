import React, { useState } from 'react';
import type { Story, StepNumber } from '../types/simple';
import { CharacterCards } from './CharacterCards';
import { CharacterChartEditor } from './CharacterChartEditor';
import { SceneTableEditor } from './SceneTableEditor';
import { SceneExpansionEditor } from './SceneExpansionEditor';
import { PDFExportEditor } from './PDFExportEditor';
import { STEP_TITLES, STEP_DESCRIPTIONS, GENERATION_ENDPOINTS, MAX_STEPS } from '../utils/constants';
import styles from '../styles/components.module.css';

interface StepContentProps {
  story: Story;
  stepNum: StepNumber;
  currentStep: number;
  onGenerate: (stepNum: StepNumber) => void;
  onRefine: (stepNumber: number, instructions: string) => void;
  onImproveScene?: (sceneNumber: number, instructions: string) => Promise<void>;
  onAdvance: () => void;
  onRollback: (targetStep: number) => void;
  onGoToCurrent: () => void;
  onNavigateToStep: (stepNum: number) => void;
  isGenerating: boolean;
  isRefining: boolean;
}

export const StepContent: React.FC<StepContentProps> = ({
  story,
  stepNum,
  currentStep,
  onGenerate,
  onRefine,
  onImproveScene,
  onAdvance,
  onRollback,
  onGoToCurrent,
  onNavigateToStep,
  isGenerating,
  isRefining
}) => {
  const title = STEP_TITLES[stepNum];
  const description = STEP_DESCRIPTIONS[stepNum];
  const content = story.steps[stepNum.toString()];
  const hasContent = content && content.trim().length > 0;
  const isCurrentStep = stepNum === story.current_step;
  const isViewingStep = stepNum === currentStep;
  const endpoint = GENERATION_ENDPOINTS[stepNum];

  // Refinement state
  const [showRefineInput, setShowRefineInput] = useState(false);
  const [refineInstructions, setRefineInstructions] = useState('');

  // Handle generate with scroll
  const handleGenerateWithScroll = (stepNum: StepNumber) => {
    onGenerate(stepNum);
    // Small delay to allow content to update, then scroll to step header
    setTimeout(() => {
      const stepHeader = document.querySelector('[class*="stepHeader"]');
      if (stepHeader) {
        stepHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };
  const [showSuccess, setShowSuccess] = useState(false);

  const handleRefineSubmit = async () => {
    if (!refineInstructions.trim()) return;
    
    // Check if this is an earlier step that has future work
    const hasFutureSteps = stepNum < story.current_step;
    
    if (hasFutureSteps) {
      const confirmed = confirm(
        `⚠️ Refining Step ${stepNum} will clear all work in later steps (${stepNum + 1}-${story.current_step}).\n\nThose steps will be permanently deleted and you'll need to regenerate them after this refinement.\n\nDo you want to continue with the refinement?`
      );
      
      if (!confirmed) {
        return; // User cancelled
      }
    }
    
    await onRefine(stepNum, refineInstructions);
    
    // Show success feedback
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 2000);
    
    // Reset refinement UI
    setShowRefineInput(false);
    setRefineInstructions('');
  };

  const handleRefineCancel = () => {
    setShowRefineInput(false);
    setRefineInstructions('');
  };

  const renderContent = () => {
    // Step 10 is special - it's always available once Step 9 is complete
    if (stepNum === 10) {
      return (
        <PDFExportEditor 
          storyId={story.story_id} 
          storySlug={story.slug} 
        />
      );
    }

    if (!hasContent || isGenerating) {
      return (
        <div className={styles.emptyContent}>
          <div className={styles.emptyContentIcon}>
            {isGenerating ? (
              <div className={styles.robotThinking}>
                <div className={styles.robotHead}>🤖</div>
                <div className={styles.typingIndicator}>
                  <div className={styles.typingDot}></div>
                  <div className={styles.typingDot}></div>
                  <div className={styles.typingDot}></div>
                </div>
              </div>
            ) : (
              '🤖'
            )}
          </div>
          <div className={styles.emptyContentTitle}>
            {isGenerating ? 'AI is thinking...' : 'Ready for AI generation'}
          </div>
          <div className={styles.emptyContentDescription}>
            {isGenerating 
              ? `Generating your ${title.toLowerCase()}...`
              : `Click "Generate Content" to let AI create your ${title.toLowerCase()}`
            }
          </div>
        </div>
      );
    }

    return (
      <div className={styles.generatedContent}>
        <div className={styles.contentHeader}>✨ AI Generated Content:</div>
        <div className={styles.contentWrapper}>
          {stepNum === 3 || stepNum === 5 ? (
            <CharacterCards content={content} />
          ) : stepNum === 7 ? (
            <CharacterChartEditor content={content} />
          ) : stepNum === 8 ? (
            <SceneTableEditor content={content} />
          ) : stepNum === 9 ? (
            <SceneExpansionEditor content={content} onImproveScene={onImproveScene} />
          ) : (
            <div className={styles.contentText}>{content}</div>
          )}
          
          {/* Success overlay */}
          {showSuccess && (
            <div className={styles.successOverlay}>
              <div className={styles.successIcon}>✓</div>
              <div className={styles.successMessage}>Refined!</div>
            </div>
          )}
        </div>

        {/* Refine Button */}
        {hasContent && !showRefineInput && !isRefining && (
          <div className={styles.refineButtonContainer}>
            <button
              className={styles.refineButton}
              onClick={() => setShowRefineInput(true)}
              disabled={isGenerating}
            >
              ✨ Refine
            </button>
          </div>
        )}

        {/* Inline Refinement Input */}
        {showRefineInput && (
          <div className={styles.refineInput}>
            <div className={styles.refineInputLabel}>
              💬 How should I refine this content?
            </div>
            <div className={styles.refineInputContainer}>
              <input
                type="text"
                className={styles.refineTextInput}
                value={refineInstructions}
                onChange={(e) => setRefineInstructions(e.target.value)}
                placeholder="e.g., 'rename the orc to Thorak' or 'make this more dramatic'"
                disabled={isRefining}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleRefineSubmit();
                  } else if (e.key === 'Escape') {
                    handleRefineCancel();
                  }
                }}
              />
              <div className={styles.refineActions}>
                <button
                  className={styles.refineSubmitButton}
                  onClick={handleRefineSubmit}
                  disabled={isRefining || !refineInstructions.trim()}
                >
                  {isRefining ? '🤖 Refining...' : 'Refine'}
                </button>
                <button
                  className={styles.refineCancelButton}
                  onClick={handleRefineCancel}
                  disabled={isRefining}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Content Actions - Only show regenerate for current step */}
        {isCurrentStep && (
          <div className={styles.contentActions}>
            <button
              className={styles.regenerateButton}
              onClick={() => handleGenerateWithScroll(stepNum)}
              disabled={isGenerating || !endpoint}
            >
              🔄 Regenerate
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={styles.stepContent}>
      <div className={styles.stepHeader}>
        <h3 className={styles.stepTitle}>Step {stepNum}: {title}</h3>
        <p className={styles.stepDescription}>{description}</p>
      </div>

      <div className={styles.contentArea}>
        {renderContent()}
      </div>
      
      {/* Show message for past steps */}
      {isViewingStep && stepNum < story.current_step && (
        <div className={styles.pastStepMessage}>
          ✓ This step is complete. You're currently on Step {story.current_step}.
          <div className={styles.pastStepActions}>
            <button
              className={styles.goToCurrentButton}
              onClick={onGoToCurrent}
            >
              Go to Step {story.current_step}
            </button>
            <button
              className={styles.rollbackButton}
              onClick={() => {
                if (confirm(`Are you sure you want to reset to Step ${stepNum}? This will permanently delete all work from Steps ${stepNum + 1}-${story.current_step}.`)) {
                  onRollback(stepNum);
                }
              }}
              disabled={isGenerating}
            >
              ↩️ Reset to this step
            </button>
          </div>
        </div>
      )}
      
      {/* Step Actions - Always show when viewing a step */}
      {isViewingStep && (
        <div className={styles.stepActions}>
          <div>
            {isCurrentStep ? (
              isGenerating ? (
                <span style={{ color: '#6c757d' }}>
                  Generating AI content...
                </span>
              ) : hasContent ? (
                <span style={{ color: '#28a745', fontWeight: '500' }}>
                  ✓ Content ready! Review and proceed or regenerate.
                </span>
              ) : (
                <span style={{ color: '#6c757d' }}>
                  Ready to generate AI content for this step.
                </span>
              )
            ) : (
              <span style={{ color: '#666' }}>
                Step {stepNum} - Navigate between completed steps or advance story.
              </span>
            )}
          </div>
          
          <div className={styles.stepActionsButtons}>
            {/* Previous Step Button */}
            {stepNum > 1 && (
              <button
                className={styles.prevStepButton}
                onClick={() => onNavigateToStep(stepNum - 1)}
                disabled={isGenerating}
              >
                ← Previous Step
              </button>
            )}
            
            {/* Generate Button - only for current step without content */}
            {isCurrentStep && !hasContent && endpoint && (
              <button
                className={styles.generateButton}
                onClick={() => handleGenerateWithScroll(stepNum)}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating...' : endpoint.buttonText}
              </button>
            )}
            
            {/* Next Step Button - only for completed steps that aren't the last */}
            {!isCurrentStep && stepNum < story.current_step && (
              <button
                className={styles.nextStepButton}
                onClick={() => onNavigateToStep(stepNum + 1)}
                disabled={isGenerating}
              >
                Next Step →
              </button>
            )}
            
            {/* Accept & Continue - only for current step with content that can advance */}
            {isCurrentStep && hasContent && stepNum < MAX_STEPS && (
              <button
                className={styles.acceptButton}
                onClick={onAdvance}
                disabled={isGenerating}
              >
                ✓ Accept & Continue
              </button>
            )}
            
            {/* Story Complete - for final step */}
            {stepNum === MAX_STEPS && hasContent && (
              <button className={styles.completeButton}>
                🎉 Story Complete!
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};