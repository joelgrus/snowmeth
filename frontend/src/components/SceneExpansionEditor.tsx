import React, { useState } from 'react';
import styles from '../styles/components.module.css';

interface SceneExpansionEditorProps {
  content: string;
  onImproveScene?: (sceneNumber: number, instructions: string) => Promise<void>;
}

interface SceneExpansionData {
  scene_number: number;
  title: string;
  pov_character: string;
  setting: string;
  scene_goal: string;
  character_goal: string;
  character_motivation: string;
  obstacles: string[];
  conflict_type: string;
  key_beats: string[];
  emotional_arc: string;
  scene_outcome: string;
  subplot_elements: string[];
  character_relationships: string;
  foreshadowing: string;
  estimated_pages: number;
}

export const SceneExpansionEditor: React.FC<SceneExpansionEditorProps> = ({ content, onImproveScene }) => {
  const [expandedScene, setExpandedScene] = useState<string | null>('scene_1');
  const [improvingScene, setImprovingScene] = useState<number | null>(null);
  const [showImproveInput, setShowImproveInput] = useState<number | null>(null);
  const [improveInstructions, setImproveInstructions] = useState('');

  const handleImproveClick = (sceneNumber: number) => {
    setShowImproveInput(sceneNumber);
    setImproveInstructions('');
  };

  const handleImproveSubmit = async (sceneNumber: number) => {
    if (!improveInstructions.trim() || !onImproveScene) return;
    
    try {
      setImprovingScene(sceneNumber);
      await onImproveScene(sceneNumber, improveInstructions);
      setShowImproveInput(null);
      setImproveInstructions('');
    } catch (error) {
      console.error('Failed to improve scene:', error);
    } finally {
      setImprovingScene(null);
    }
  };

  const handleImproveCancel = () => {
    setShowImproveInput(null);
    setImproveInstructions('');
  };

  const renderSceneExpansions = () => {
    try {
      // Parse the scene expansions data (expected to be JSON object with scene_1, scene_2, etc.)
      const sceneExpansions = JSON.parse(content);
      
      if (typeof sceneExpansions !== 'object' || sceneExpansions === null) {
        throw new Error('Scene expansions should be an object');
      }

      const sceneKeys = Object.keys(sceneExpansions).sort((a, b) => {
        const numA = parseInt(a.replace('scene_', ''));
        const numB = parseInt(b.replace('scene_', ''));
        return numA - numB;
      });

      return (
        <div className={styles.sceneExpansions}>
          {sceneKeys.map((sceneKey) => {
            const scene: SceneExpansionData = sceneExpansions[sceneKey];
            const isExpanded = expandedScene === sceneKey;
            
            return (
              <div key={sceneKey} className={styles.sceneExpansionCard}>
                <div 
                  className={styles.sceneExpansionHeader}
                  onClick={() => setExpandedScene(isExpanded ? null : sceneKey)}
                >
                  <div className={styles.sceneExpansionTitle}>
                    <div className={styles.sceneExpansionNumber}>
                      Scene {scene.scene_number}
                    </div>
                    <div className={styles.sceneExpansionTitleText}>
                      {scene.title}
                    </div>
                  </div>
                  <div className={styles.sceneExpansionMeta}>
                    <span className={styles.sceneExpansionPOV}>
                      POV: {scene.pov_character}
                    </span>
                    <span className={styles.sceneExpansionPages}>
                      ~{scene.estimated_pages} pages
                    </span>
                    <div className={styles.sceneExpansionToggle}>
                      {isExpanded ? '−' : '+'}
                    </div>
                  </div>
                </div>
                
                {isExpanded && (
                  <div className={styles.sceneExpansionContent}>
                    <div className={styles.sceneExpansionGrid}>
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Setting</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.setting}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Scene Goal</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.scene_goal}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Character Goal</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.character_goal}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Character Motivation</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.character_motivation}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Obstacles</h4>
                        <ul className={styles.sceneExpansionList}>
                          {scene.obstacles.map((obstacle, index) => (
                            <li key={index} className={styles.sceneExpansionListItem}>
                              {obstacle}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Conflict Type</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.conflict_type}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Key Story Beats</h4>
                        <ul className={styles.sceneExpansionList}>
                          {scene.key_beats.map((beat, index) => (
                            <li key={index} className={styles.sceneExpansionListItem}>
                              {beat}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Emotional Arc</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.emotional_arc}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Scene Outcome</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.scene_outcome}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Subplot Elements</h4>
                        <ul className={styles.sceneExpansionList}>
                          {scene.subplot_elements.map((element, index) => (
                            <li key={index} className={styles.sceneExpansionListItem}>
                              {element}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Character Relationships</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.character_relationships}</p>
                      </div>
                      
                      <div className={styles.sceneExpansionSection}>
                        <h4 className={styles.sceneExpansionSectionTitle}>Foreshadowing</h4>
                        <p className={styles.sceneExpansionSectionContent}>{scene.foreshadowing}</p>
                      </div>
                    </div>
                    
                    {/* Scene Actions */}
                    <div className={styles.sceneExpansionActions}>
                      {showImproveInput === scene.scene_number ? (
                        <div className={styles.sceneImproveInput}>
                          <div className={styles.sceneImproveLabel}>
                            💬 How should I improve this scene?
                          </div>
                          <div className={styles.sceneImproveContainer}>
                            <input
                              type="text"
                              className={styles.sceneImproveTextInput}
                              value={improveInstructions}
                              onChange={(e) => setImproveInstructions(e.target.value)}
                              placeholder="e.g., 'add more tension', 'clarify character motivation', 'enhance the setting'"
                              disabled={improvingScene === scene.scene_number}
                              autoFocus
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  handleImproveSubmit(scene.scene_number);
                                } else if (e.key === 'Escape') {
                                  handleImproveCancel();
                                }
                              }}
                            />
                            <div className={styles.sceneImproveActions}>
                              <button
                                className={styles.sceneImproveSubmitButton}
                                onClick={() => handleImproveSubmit(scene.scene_number)}
                                disabled={improvingScene === scene.scene_number || !improveInstructions.trim()}
                              >
                                {improvingScene === scene.scene_number ? '🤖 Improving...' : 'Improve'}
                              </button>
                              <button
                                className={styles.sceneImproveCancelButton}
                                onClick={handleImproveCancel}
                                disabled={improvingScene === scene.scene_number}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <button 
                          className={styles.improveSceneButton}
                          onClick={() => handleImproveClick(scene.scene_number)}
                          disabled={improvingScene !== null || !onImproveScene}
                        >
                          {improvingScene === scene.scene_number ? '🤖 Improving...' : '✨ Improve This Scene'}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      );
    } catch (error) {
      console.error('Error parsing scene expansions:', error);
      // Fallback to raw text if JSON parsing fails
      return (
        <div className={styles.contentText}>
          {content}
        </div>
      );
    }
  };

  return renderSceneExpansions();
};