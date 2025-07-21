import React, { useState } from 'react';
import type { StoryCreateRequest } from '../types/simple';
import styles from '../styles/components.module.css';

interface NewStoryFormProps {
  onSubmit: (request: StoryCreateRequest) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export const NewStoryForm: React.FC<NewStoryFormProps> = ({
  onSubmit,
  onCancel,
  isSubmitting
}) => {
  const [slug, setSlug] = useState('');
  const [storyIdea, setStoryIdea] = useState('');

  const handleSubmit = () => {
    if (slug.trim() && storyIdea.trim()) {
      onSubmit({
        slug: slug.trim(),
        story_idea: storyIdea.trim()
      });
    }
  };

  const canSubmit = slug.trim() && storyIdea.trim() && !isSubmitting;

  return (
    <div className={styles.newStoryForm}>
      <h3 className={styles.newStoryTitle}>Create New Story</h3>
      
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>
          Story Title/Slug:
        </label>
        <input
          className={styles.formInput}
          type="text"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          placeholder="e.g. my-fantasy-novel"
          disabled={isSubmitting}
        />
      </div>
      
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>
          Story Idea:
        </label>
        <textarea
          className={styles.formTextarea}
          value={storyIdea}
          onChange={(e) => setStoryIdea(e.target.value)}
          placeholder="Describe your story idea in a few sentences..."
          rows={3}
          disabled={isSubmitting}
        />
      </div>
      
      <div className={styles.formActions}>
        <button
          className={styles.createButton}
          onClick={handleSubmit}
          disabled={!canSubmit}
        >
          {isSubmitting ? 'Creating...' : 'Create Story'}
        </button>
        <button
          className={styles.cancelButton}
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>
      </div>
    </div>
  );
};