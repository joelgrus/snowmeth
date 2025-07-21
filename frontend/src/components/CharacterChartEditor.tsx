import React, { useState } from 'react';
import styles from '../styles/components.module.css';

interface CharacterChartEditorProps {
  content: string;
}

interface CharacterChart {
  [characterName: string]: string;
}

export const CharacterChartEditor: React.FC<CharacterChartEditorProps> = ({ content }) => {
  const [expandedCharacter, setExpandedCharacter] = useState<string | null>(null);

  const renderCharacterCharts = () => {
    try {
      // Clean up potential markdown formatting
      let cleanContent = content.trim();
      if (cleanContent.startsWith('```json')) {
        cleanContent = cleanContent.replace(/^```json\s*/, '').replace(/\s*```$/, '');
      } else if (cleanContent.startsWith('```')) {
        cleanContent = cleanContent.replace(/^```\s*/, '').replace(/\s*```$/, '');
      }
      
      const characterCharts: CharacterChart = JSON.parse(cleanContent);
      
      return (
        <div className={styles.characterCharts}>
          {Object.entries(characterCharts).map(([characterName, chart]) => (
            <div key={characterName} className={styles.characterChartCard}>
              <div 
                className={styles.characterChartHeader}
                onClick={() => setExpandedCharacter(
                  expandedCharacter === characterName ? null : characterName
                )}
              >
                <h4 className={styles.characterChartName}>{characterName}</h4>
                <div className={styles.characterChartToggle}>
                  {expandedCharacter === characterName ? '−' : '+'}
                </div>
              </div>
              
              {expandedCharacter === characterName && (
                <div className={styles.characterChartContent}>
                  <div className={styles.characterChartText}>
                    {chart}
                  </div>
                </div>
              )}
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

  return renderCharacterCharts();
};