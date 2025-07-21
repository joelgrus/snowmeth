import React from 'react';
import styles from '../styles/components.module.css';

interface SceneTableEditorProps {
  content: string;
}

interface SceneData {
  scene_number: number;
  pov_character: string;
  scene_description: string;
  estimated_pages: number;
}

export const SceneTableEditor: React.FC<SceneTableEditorProps> = ({ content }) => {
  const renderSceneTable = () => {
    try {
      // The AI should generate clean JSON, but handle basic cleanup just in case
      let cleanContent = content.trim();
      
      // Remove markdown code blocks if present
      if (cleanContent.startsWith('```json') && cleanContent.endsWith('```')) {
        cleanContent = cleanContent.slice(7, -3).trim();
      } else if (cleanContent.startsWith('```') && cleanContent.endsWith('```')) {
        cleanContent = cleanContent.slice(3, -3).trim();
      }
      
      const scenes: SceneData[] = JSON.parse(cleanContent);
      
      if (!Array.isArray(scenes)) {
        throw new Error('Scene data should be an array');
      }
      
      return (
        <div className={styles.sceneTable}>
          {scenes.map((scene) => (
            <div key={scene.scene_number} className={styles.sceneCard}>
              <div className={styles.sceneHeader}>
                <div className={styles.sceneNumber}>
                  Scene {scene.scene_number}
                </div>
                <div className={styles.sceneMetadata}>
                  <span className={styles.povCharacter}>
                    POV: {scene.pov_character}
                  </span>
                  <span className={styles.estimatedPages}>
                    ~{scene.estimated_pages} pages
                  </span>
                </div>
              </div>
              
              <div className={styles.sceneDescription}>
                {scene.scene_description}
              </div>
            </div>
          ))}
          
          <div className={styles.sceneTableSummary}>
            <div className={styles.summaryText}>
              <strong>Total Scenes:</strong> {scenes.length} | 
              <strong> Estimated Pages:</strong> {scenes.reduce((total, scene) => total + scene.estimated_pages, 0)}
            </div>
          </div>
        </div>
      );
    } catch (error) {
      // Fallback to raw text if JSON parsing fails
      return (
        <div className={styles.contentText}>
          {content}
        </div>
      );
    }
  };

  return renderSceneTable();
};