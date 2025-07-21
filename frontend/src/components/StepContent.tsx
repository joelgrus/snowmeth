import React from 'react';
import type { Story, StepNumber } from '../types/simple';
import { CharacterCards } from './CharacterCards';
import { STEP_TITLES, STEP_DESCRIPTIONS, GENERATION_ENDPOINTS, MAX_STEPS } from '../utils/constants';
import styles from '../styles/components.module.css';

interface StepContentProps {
  story: Story;
  stepNum: StepNumber;
  currentStep: number;
  onGenerate: (stepNum: StepNumber) => void;
  onAdvance: () => void;
  onRollback: (targetStep: number) => void;
  onGoToCurrent: () => void;
  isGenerating: boolean;
}

export const StepContent: React.FC<StepContentProps> = ({
  story,
  stepNum,
  currentStep,
  onGenerate,
  onAdvance,
  onRollback,
  onGoToCurrent,
  isGenerating
}) => {
  const title = STEP_TITLES[stepNum];
  const description = STEP_DESCRIPTIONS[stepNum];
  const content = story.steps[stepNum.toString()];
  const hasContent = content && content.trim().length > 0;
  const isCurrentStep = stepNum === story.current_step;
  const isViewingStep = stepNum === currentStep;
  const endpoint = GENERATION_ENDPOINTS[stepNum];

  const renderContent = () => {
    if (!hasContent) {
      return (
        <div className={styles.emptyContent}>
          <div className={`${styles.emptyContentIcon} ${isGenerating ? styles.generating : ''}`}>
            {isGenerating ? '🤖💭' : '🤖'}
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
        {(stepNum === 3 || stepNum === 5) ? (
          <CharacterCards content={content} />
        ) : (
          <div className={styles.contentText}>{content}</div>
        )}
        
        {/* Content Actions */}
        {isCurrentStep && (
          <div className={styles.contentActions}>
            <button
              className={styles.acceptButton}
              onClick={onAdvance}
              disabled={isGenerating}
            >
              ✓ Accept & Continue
            </button>
            <button
              className={styles.regenerateButton}
              onClick={() => onGenerate(stepNum)}
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
                if (confirm(`Are you sure you want to go back to Step ${stepNum}? This will clear all work from Steps ${stepNum + 1}-${story.current_step}.`)) {
                  onRollback(stepNum);
                }
              }}
              disabled={isGenerating}
            >
              ↩️ Go Back Here
            </button>
          </div>
        </div>
      )}
      
      {/* Current Step Actions */}
      {isViewingStep && isCurrentStep && (
        <div className={styles.stepActions}>
          <div>
            {hasContent ? (
              <span style={{ color: '#28a745', fontWeight: '500' }}>
                ✓ Content ready! Review and proceed or regenerate.
              </span>
            ) : (
              <span style={{ color: '#6c757d' }}>
                Generate AI content for this step to proceed.
              </span>
            )}
          </div>
          
          <div className={styles.stepActionsButtons}>
            {!hasContent && endpoint && (
              <button
                className={styles.generateButton}
                onClick={() => onGenerate(stepNum)}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating...' : endpoint.buttonText}
              </button>
            )}
            
            {hasContent && stepNum < MAX_STEPS && (
              <button
                className={styles.nextStepButton}
                onClick={onAdvance}
                disabled={isGenerating}
              >
                {isGenerating ? 'Processing...' : 'Next Step →'}
              </button>
            )}
            
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