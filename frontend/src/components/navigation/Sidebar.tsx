import React from 'react';
import { CheckCircle, Circle, ArrowRight, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';
import { Story } from '../../types';
import { SNOWFLAKE_STEPS } from '../../utils/constants';

interface SidebarProps {
  story: Story | null;
  currentStep: number;
  onStepClick: (step: number) => void;
  collapsed: boolean;
}

export function Sidebar({ story, currentStep, onStepClick, collapsed }: SidebarProps) {
  if (!story) return null;

  const getStepStatus = (stepId: number) => {
    const hasContent = story.steps[stepId.toString()];
    const isCurrentStep = stepId === story.current_step;
    const isCompleted = hasContent && stepId < story.current_step;
    const canAccess = stepId <= story.current_step;

    return {
      isCompleted,
      isCurrentStep,
      canAccess,
      hasContent: !!hasContent,
    };
  };

  const getStepIcon = (stepId: number) => {
    const status = getStepStatus(stepId);
    
    if (status.isCompleted) {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    }
    
    if (status.isCurrentStep) {
      return <ArrowRight className="w-5 h-5 text-blue-600" />;
    }
    
    if (!status.canAccess) {
      return <Circle className="w-5 h-5 text-gray-300" />;
    }
    
    return <Circle className="w-5 h-5 text-gray-400" />;
  };

  const calculateProgress = () => {
    const completedSteps = SNOWFLAKE_STEPS.filter(step => 
      getStepStatus(step.id).isCompleted
    ).length;
    return (completedSteps / SNOWFLAKE_STEPS.length) * 100;
  };

  return (
    <div className={clsx(
      'bg-white border-r border-gray-200 flex flex-col transition-all duration-300',
      collapsed ? 'w-16' : 'w-80'
    )}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        {!collapsed && (
          <>
            <h2 className="font-semibold text-gray-900 truncate">
              {story.slug}
            </h2>
            <p className="text-sm text-gray-500 mt-1 truncate">
              {story.story_idea}
            </p>
            
            {/* Progress Bar */}
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Progress</span>
                <span>{Math.round(calculateProgress())}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${calculateProgress()}%` }}
                />
              </div>
            </div>
          </>
        )}
      </div>

      {/* Steps */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-1">
          {SNOWFLAKE_STEPS.map((step) => {
            const status = getStepStatus(step.id);
            
            return (
              <button
                key={step.id}
                onClick={() => status.canAccess && onStepClick(step.id)}
                disabled={!status.canAccess}
                className={clsx(
                  'w-full flex items-center p-3 rounded-lg text-left transition-colors',
                  status.canAccess
                    ? 'hover:bg-gray-50 cursor-pointer'
                    : 'cursor-not-allowed opacity-50',
                  status.isCurrentStep && 'bg-blue-50 border border-blue-200',
                  collapsed && 'justify-center'
                )}
              >
                <div className="flex-shrink-0">
                  {getStepIcon(step.id)}
                </div>
                
                {!collapsed && (
                  <div className="ml-3 flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className={clsx(
                        'text-sm font-medium truncate',
                        status.isCurrentStep ? 'text-blue-900' : 'text-gray-900'
                      )}>
                        Step {step.id}: {step.title}
                      </p>
                      {status.hasContent && !status.isCompleted && (
                        <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className={clsx(
                      'text-xs truncate mt-1',
                      status.isCurrentStep ? 'text-blue-700' : 'text-gray-500'
                    )}>
                      {step.description}
                    </p>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Analysis Button */}
      {!collapsed && story.current_step >= 6 && (
        <div className="p-4 border-t border-gray-200">
          <button className="w-full btn-secondary text-sm">
            Analyze Story
          </button>
        </div>
      )}
    </div>
  );
}