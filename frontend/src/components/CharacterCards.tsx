import React from 'react';
import styles from '../styles/components.module.css';

interface CharacterCardsProps {
  content: string;
}

export const CharacterCards: React.FC<CharacterCardsProps> = ({ content }) => {
  const renderCharacterCards = () => {
    try {
      // Clean up potential markdown formatting
      let cleanContent = content.trim();
      if (cleanContent.startsWith('```json')) {
        cleanContent = cleanContent.replace(/^```json\s*/, '').replace(/\s*```$/, '');
      } else if (cleanContent.startsWith('```')) {
        cleanContent = cleanContent.replace(/^```\s*/, '').replace(/\s*```$/, '');
      }
      
      const characters = JSON.parse(cleanContent);
      
      return (
        <div className={styles.characterCards}>
          {Object.entries(characters).map(([name, summary]) => (
            <div key={name} className={styles.characterCard}>
              <h4 className={styles.characterName}>{name}</h4>
              <p className={styles.characterSummary}>
                {String(summary)}
              </p>
            </div>
          ))}
        </div>
      );
    } catch {
      // Fallback to raw text if JSON parsing fails
      return (
        <div className={styles.contentText}>
          {content}
        </div>
      );
    }
  };

  return renderCharacterCards();
};