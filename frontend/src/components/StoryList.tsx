import React from 'react';
import type { Story } from '../types/simple';
import styles from '../styles/components.module.css';

interface StoryListProps {
  stories: Story[];
  onSelectStory: (story: Story) => void;
  onDeleteStory: (storyId: string) => void;
  onNewStory: () => void;
  isDeleting: boolean;
}

export const StoryList: React.FC<StoryListProps> = ({
  stories,
  onSelectStory,
  onDeleteStory,
  onNewStory,
  isDeleting
}) => {
  const handleDeleteClick = (e: React.MouseEvent, storyId: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this story? This cannot be undone.')) {
      onDeleteStory(storyId);
    }
  };

  return (
    <div>
      <div className={styles.storyListHeader}>
        <h2 className={styles.storyListTitle}>Your Stories</h2>
        <button 
          className={styles.newStoryButton}
          onClick={onNewStory}
        >
          + New Story
        </button>
      </div>

      <div className={styles.storiesList}>
        {stories.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyStateIcon}>📚</div>
            <p>No stories yet. Click "New Story" to get started!</p>
          </div>
        ) : (
          stories.map((story, index) => (
            <div 
              key={story.story_id} 
              className={styles.storyItem}
              style={{
                '--animation-delay': index
              } as React.CSSProperties}
            >
              <div
                className={styles.storyContent}
                onClick={() => onSelectStory(story)}
              >
                <div className={styles.storySlug}>{story.slug}</div>
                <div className={styles.storyIdea}>{story.story_idea}</div>
                
                {/* Progress Bar */}
                <div className={styles.progressContainer}>
                  <div className={styles.progressLabel}>
                    <span>Progress</span>
                    <span className={styles.progressPercentage}>
                      {Math.round((story.current_step / 10) * 100)}%
                    </span>
                  </div>
                  <div className={styles.progressBar}>
                    <div 
                      className={styles.progressFill}
                      style={{ width: `${(story.current_step / 10) * 100}%` }}
                    />
                  </div>
                </div>
                
                <div className={styles.storyProgress}>
                  Step {story.current_step} of 10
                </div>
              </div>
              
              <div className={styles.storyActions}>
                <button
                  className={styles.deleteButton}
                  onClick={(e) => handleDeleteClick(e, story.story_id)}
                  disabled={isDeleting}
                  title="Delete story"
                >
                  <span className={styles.deleteIcon}>🗑️</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};