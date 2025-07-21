import React from 'react';
import { Story } from '../types';
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
          stories.map((story) => (
            <div key={story.story_id} className={styles.storyItem}>
              <div
                className={styles.storyContent}
                onClick={() => onSelectStory(story)}
              >
                <div className={styles.storySlug}>{story.slug}</div>
                <div className={styles.storyIdea}>{story.story_idea}</div>
                <div className={styles.storyProgress}>
                  Step {story.current_step} of 10
                </div>
              </div>
              <button
                className={styles.deleteButton}
                onClick={(e) => handleDeleteClick(e, story.story_id)}
                disabled={isDeleting}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};