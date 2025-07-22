import React from 'react';
import type { Story, StepNumber } from '../types/simple';
import { STEP_TITLES, MAX_STEPS } from '../utils/constants';
import styles from '../styles/components.module.css';

interface StepNavigationProps {
  story: Story;
  currentStep: number;
  onStepChange: (stepNum: number) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  story,
  currentStep,
  onStepChange,
  collapsed = false,
  onToggleCollapse
}) => {
  const steps = Array.from({ length: MAX_STEPS }, (_, i) => i + 1);

  return (
    <div className={`${styles.stepNavigation} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.stepNavigationHeader}>
        <h3 className={styles.stepNavigationTitle}>Steps</h3>
        {onToggleCollapse && (
          <button 
            className={styles.navigationToggle}
            onClick={onToggleCollapse}
            aria-label="Toggle navigation"
          >
            {collapsed ? '▶' : '◀'}
          </button>
        )}
      </div>
      {steps.map((stepNum) => {
        const isCurrent = stepNum === currentStep;
        const isCompleted = stepNum < story.current_step;
        const canAccess = stepNum <= story.current_step;
        
        const buttonClass = [
          styles.stepButton,
          isCurrent && styles.stepButtonCurrent,
          isCompleted && styles.stepButtonCompleted
        ].filter(Boolean).join(' ');
        
        return (
          <button
            key={stepNum}
            className={buttonClass}
            onClick={() => canAccess && onStepChange(stepNum)}
            disabled={!canAccess}
          >
            <div className={styles.stepButtonTitle}>
              Step {stepNum} {isCompleted ? '✓' : isCurrent ? '→' : '○'}
            </div>
            <div className={styles.stepButtonSubtitle}>
              {STEP_TITLES[stepNum as StepNumber]}
            </div>
          </button>
        );
      })}
    </div>
  );
};