import React, { useState, useEffect } from 'react';

interface Character {
  name: string;
  description: string;
}

interface Story {
  story_id: string;
  slug: string;
  story_idea: string;
  current_step: number;
  steps: Record<string, any>;
}


function App() {
  const [stories, setStories] = useState<Story[]>([]);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [loadingStory, setLoadingStory] = useState(false);
  const [advancing, setAdvancing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showNewStoryForm, setShowNewStoryForm] = useState(false);
  const [newStorySlug, setNewStorySlug] = useState('');
  const [newStoryIdea, setNewStoryIdea] = useState('');

  useEffect(() => {
    fetchStories();
  }, []);

  const fetchStories = async () => {
    try {
      const response = await fetch('/api/stories');
      if (!response.ok) throw new Error('Failed to fetch stories');
      const data = await response.json();
      setStories(data.stories);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLoading(false);
    }
  };

  const selectStory = async (story: Story) => {
    setLoadingStory(true);
    setError(null);
    try {
      // Fetch full story details
      const response = await fetch(`/api/stories/${story.story_id}`);
      if (!response.ok) throw new Error('Failed to fetch story details');
      const fullStory = await response.json();
      setSelectedStory(fullStory);
      setCurrentStep(fullStory.current_step);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load story');
    } finally {
      setLoadingStory(false);
    }
  };

  const getStepTitle = (stepNum: number): string => {
    const titles = {
      1: 'One Sentence Summary',
      2: 'One Paragraph Summary',
      3: 'Characters',
      4: 'Story Structure',
      5: 'Character Synopses',
      6: 'Detailed Story Synopsis',
      7: 'Character Charts',
      8: 'Scene List',
      9: 'Scene Narratives',
      10: 'First Draft'
    };
    return titles[stepNum as keyof typeof titles] || `Step ${stepNum}`;
  };

  const getStepDescription = (stepNum: number): string => {
    const descriptions = {
      1: 'Summarize your story in one sentence',
      2: 'Expand your sentence into a paragraph',
      3: 'List your main characters',
      4: 'Expand each plot point into a paragraph',
      5: 'Write a one-page synopsis for each character',
      6: 'Expand your story structure into multiple pages',
      7: 'Create detailed character development charts',
      8: 'Create a spreadsheet of scenes',
      9: 'Write narrative descriptions for each scene',
      10: 'Write your first draft'
    };
    return descriptions[stepNum as keyof typeof descriptions] || '';
  };

  const generateParagraphSummary = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/generate_paragraph_summary`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to generate paragraph summary');
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate paragraph summary');
    } finally {
      setAdvancing(false);
    }
  };

  const generateCharacters = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/generate_characters`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to generate characters');
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate characters');
    } finally {
      setAdvancing(false);
    }
  };

  const generatePlotStructure = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/generate_plot_structure`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to generate plot structure');
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate plot structure');
    } finally {
      setAdvancing(false);
    }
  };

  const generateCharacterSynopses = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/generate_character_synopses`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to generate character synopses');
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate character synopses');
    } finally {
      setAdvancing(false);
    }
  };

  const generateDetailedSynopsis = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/generate_detailed_synopsis`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to generate detailed synopsis');
      
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate detailed synopsis');
    } finally {
      setAdvancing(false);
    }
  };

  const createStory = async () => {
    if (!newStorySlug.trim() || !newStoryIdea.trim() || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch('/api/stories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          slug: newStorySlug.trim(),
          story_idea: newStoryIdea.trim(),
        }),
      });
      
      if (!response.ok) throw new Error('Failed to create story');
      
      const newStory = await response.json();
      
      // Refresh the stories list
      await fetchStories();
      
      // Select the new story and go to step 1
      setSelectedStory(newStory);
      setCurrentStep(1);
      
      // Reset form
      setShowNewStoryForm(false);
      setNewStorySlug('');
      setNewStoryIdea('');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create story');
    } finally {
      setAdvancing(false);
    }
  };

  const deleteStory = async (storyId: string) => {
    if (advancing) return;
    
    if (!confirm('Are you sure you want to delete this story? This cannot be undone.')) {
      return;
    }
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${storyId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete story');
      
      // If we're currently viewing this story, go back to story list
      if (selectedStory && selectedStory.story_id === storyId) {
        setSelectedStory(null);
      }
      
      // Refresh the stories list
      await fetchStories();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete story');
    } finally {
      setAdvancing(false);
    }
  };

  const advanceToNextStep = async () => {
    if (!selectedStory || advancing) return;
    
    setAdvancing(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/stories/${selectedStory.story_id}/next`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to advance story');
      
      // Get the updated story
      const updatedStory = await response.json();
      setSelectedStory(updatedStory);
      
      // Move to the new step
      setCurrentStep(updatedStory.current_step);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to advance story');
    } finally {
      setAdvancing(false);
    }
  };

  const renderStepContent = (story: Story, stepNum: number) => {
    const title = getStepTitle(stepNum);
    const description = getStepDescription(stepNum);
    const content = story.steps[stepNum.toString()];
    const hasContent = content && content.trim().length > 0;
    const isCurrentStep = stepNum === story.current_step;
    const isViewingStep = stepNum === currentStep;

    return (
      <div>
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 8px 0' }}>
            Step {stepNum}: {title}
          </h3>
          <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
            {description}
          </p>
        </div>

        {/* AI-Generated Content Display */}
        <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '8px', border: '1px solid #ddd', minHeight: '200px' }}>
          {hasContent ? (
            <div>
              <div style={{ 
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '6px',
                border: '1px solid #e9ecef',
                marginBottom: '16px'
              }}>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: '500' }}>
                  ✨ AI Generated Content:
                </div>
                {(stepNum === 3 || stepNum === 5) ? (
                  // Special display for character JSON (Step 3: Characters, Step 5: Character Synopses)
                  <div>
                    {(() => {
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
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {Object.entries(characters).map(([name, summary]) => (
                              <div key={name} style={{
                                padding: '16px',
                                border: '1px solid #ddd',
                                borderRadius: '8px',
                                backgroundColor: '#fff'
                              }}>
                                <h4 style={{ margin: '0 0 12px 0', color: '#2196f3' }}>{name}</h4>
                                <p style={{ 
                                  margin: 0, 
                                  fontSize: '14px', 
                                  lineHeight: '1.6',
                                  whiteSpace: 'pre-wrap'
                                }}>
                                  {String(summary)}
                                </p>
                              </div>
                            ))}
                          </div>
                        );
                      } catch {
                        // Fallback to raw text if JSON parsing fails
                        return (
                          <div style={{ 
                            fontSize: '16px', 
                            lineHeight: '1.6',
                            whiteSpace: 'pre-wrap'
                          }}>
                            {content}
                          </div>
                        );
                      }
                    })()}
                  </div>
                ) : (
                  // Regular text display for other steps
                  <div style={{ 
                    fontSize: '16px', 
                    lineHeight: '1.6',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {content}
                  </div>
                )}
              </div>
              
              {/* Content Actions */}
              {isCurrentStep && (
                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                  <button
                    onClick={advanceToNextStep}
                    disabled={advancing}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: advancing ? '#6c757d' : '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: advancing ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    ✓ Accept & Continue
                  </button>
                  <button
                    onClick={() => {
                      if (stepNum === 2) {
                        generateParagraphSummary();
                      } else if (stepNum === 3) {
                        generateCharacters();
                      } else if (stepNum === 4) {
                        generatePlotStructure();
                      } else if (stepNum === 5) {
                        generateCharacterSynopses();
                      } else if (stepNum === 6) {
                        generateDetailedSynopsis();
                      } else {
                        setError(`Regeneration not yet implemented for Step ${stepNum}`);
                      }
                    }}
                    disabled={advancing}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: advancing ? '#6c757d' : '#ffc107',
                      color: advancing ? 'white' : '#212529',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: advancing ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    🔄 Regenerate
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '150px',
              color: '#6c757d',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
              <div style={{ fontSize: '16px', marginBottom: '8px' }}>
                Ready for AI generation
              </div>
              <div style={{ fontSize: '14px' }}>
                Click "Generate Content" to let AI create your {title.toLowerCase()}
              </div>
            </div>
          )}
        </div>
        
        {/* Show message for past steps */}
        {isViewingStep && stepNum < story.current_step && (
          <div style={{ 
            marginTop: '16px', 
            padding: '16px', 
            backgroundColor: '#e8f5e9', 
            borderRadius: '8px',
            fontSize: '14px'
          }}>
            ✓ This step is complete. You're currently on Step {story.current_step}.
            <button
              onClick={() => setCurrentStep(story.current_step)}
              style={{
                marginLeft: '12px',
                padding: '6px 12px',
                backgroundColor: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Go to Step {story.current_step}
            </button>
          </div>
        )}
        
        {/* Current Step Actions */}
        {isViewingStep && isCurrentStep && (
          <div style={{ 
            marginTop: '24px', 
            padding: '16px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
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
            
            <div style={{ display: 'flex', gap: '12px' }}>
              {!hasContent && (
                <button
                  onClick={() => {
                    if (stepNum === 2) {
                      generateParagraphSummary();
                    } else if (stepNum === 3) {
                      generateCharacters();
                    } else if (stepNum === 4) {
                      generatePlotStructure();
                    } else if (stepNum === 5) {
                      generateCharacterSynopses();
                    } else if (stepNum === 6) {
                      generateDetailedSynopsis();
                    } else {
                      setError(`Generation not yet implemented for Step ${stepNum}`);
                    }
                  }}
                  disabled={advancing}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: advancing ? '#6c757d' : '#2196f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: advancing ? 'not-allowed' : 'pointer',
                    fontWeight: '500',
                    fontSize: '14px'
                  }}
                >
                  {advancing ? 'Generating...' : 
                    stepNum === 2 ? '✨ Generate Paragraph' :
                    stepNum === 3 ? '✨ Generate Characters' :
                    stepNum === 4 ? '✨ Generate Plot Structure' :
                    stepNum === 5 ? '✨ Generate Character Synopses' :
                    stepNum === 6 ? '✨ Generate Detailed Synopsis' :
                    '✨ Generate Content'}
                </button>
              )}
              
              {hasContent && stepNum < 10 && (
                <button
                  onClick={advanceToNextStep}
                  disabled={advancing}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: advancing ? '#6c757d' : '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: advancing ? 'not-allowed' : 'pointer',
                    fontWeight: '500',
                    fontSize: '14px'
                  }}
                >
                  {advancing ? 'Processing...' : 'Next Step →'}
                </button>
              )}
              
              {stepNum === 10 && hasContent && (
                <button
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#6f42c1',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '500',
                    fontSize: '14px'
                  }}
                >
                  🎉 Story Complete!
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading stories...</div>;
  if (loadingStory) return <div style={{ padding: '20px' }}>Loading story details...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Snowflake Method - Simple Version</h1>
      
      {error && (
        <div style={{ padding: '10px', marginBottom: '20px', backgroundColor: '#ffebee', color: '#c62828', borderRadius: '5px' }}>
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: '10px', padding: '2px 8px' }}>×</button>
        </div>
      )}
      
      {!selectedStory ? (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>Your Stories</h2>
            <button
              onClick={() => setShowNewStoryForm(true)}
              style={{
                padding: '10px 20px',
                backgroundColor: '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              + New Story
            </button>
          </div>

          {showNewStoryForm && (
            <div style={{
              padding: '20px',
              border: '2px solid #2196f3',
              borderRadius: '8px',
              backgroundColor: '#f8f9ff',
              marginBottom: '20px',
              maxWidth: '500px'
            }}>
              <h3 style={{ margin: '0 0 16px 0' }}>Create New Story</h3>
              
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Story Title/Slug:
                </label>
                <input
                  type="text"
                  value={newStorySlug}
                  onChange={(e) => setNewStorySlug(e.target.value)}
                  placeholder="e.g. my-fantasy-novel"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              </div>
              
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Story Idea:
                </label>
                <textarea
                  value={newStoryIdea}
                  onChange={(e) => setNewStoryIdea(e.target.value)}
                  placeholder="Describe your story idea in a few sentences..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={createStory}
                  disabled={!newStorySlug.trim() || !newStoryIdea.trim() || advancing}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: (!newStorySlug.trim() || !newStoryIdea.trim() || advancing) ? '#ccc' : '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: (!newStorySlug.trim() || !newStoryIdea.trim() || advancing) ? 'not-allowed' : 'pointer',
                    fontWeight: '500'
                  }}
                >
                  {advancing ? 'Creating...' : 'Create Story'}
                </button>
                <button
                  onClick={() => {
                    setShowNewStoryForm(false);
                    setNewStorySlug('');
                    setNewStoryIdea('');
                  }}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '500px' }}>
            {stories.length === 0 ? (
              <div style={{
                padding: '40px',
                textAlign: 'center',
                color: '#666',
                border: '2px dashed #ddd',
                borderRadius: '8px'
              }}>
                <div style={{ fontSize: '24px', marginBottom: '16px' }}>📚</div>
                <p>No stories yet. Click "New Story" to get started!</p>
              </div>
            ) : (
              stories.map((story) => (
                <div
                  key={story.story_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '15px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    backgroundColor: '#fff'
                  }}
                >
                  <div
                    onClick={() => selectStory(story)}
                    style={{
                      flex: 1,
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{story.slug}</div>
                    <div style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>{story.story_idea}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>Step {story.current_step} of 10</div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteStory(story.story_id);
                    }}
                    disabled={advancing}
                    style={{
                      padding: '6px 10px',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: advancing ? 'not-allowed' : 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Delete
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={() => setSelectedStory(null)}
              style={{ padding: '5px 10px', marginRight: '10px' }}
            >
              ← Back to Stories
            </button>
            <h2>{selectedStory.slug}</h2>
            <p style={{ color: '#666' }}>{selectedStory.story_idea}</p>
          </div>

          <div style={{ display: 'flex', gap: '20px', minHeight: '600px' }}>
            {/* Steps Sidebar */}
            <div style={{ width: '280px', flexShrink: 0, backgroundColor: '#f5f5f5', padding: '15px', borderRadius: '5px' }}>
              <h3 style={{ margin: '0 0 16px 0' }}>Steps</h3>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((stepNum) => {
                const hasContent = selectedStory.steps[stepNum.toString()];
                const isCurrent = stepNum === currentStep;
                const isCompleted = stepNum < selectedStory.current_step;
                const canAccess = stepNum <= selectedStory.current_step;
                
                return (
                  <button
                    key={stepNum}
                    onClick={() => canAccess && setCurrentStep(stepNum)}
                    disabled={!canAccess}
                    style={{
                      width: '100%',
                      padding: '12px',
                      margin: '4px 0',
                      backgroundColor: isCurrent ? '#e3f2fd' : isCompleted ? '#e8f5e8' : '#fff',
                      border: isCurrent ? '2px solid #2196f3' : '1px solid #ddd',
                      borderRadius: '6px',
                      fontSize: '14px',
                      textAlign: 'left',
                      cursor: canAccess ? 'pointer' : 'not-allowed',
                      opacity: canAccess ? 1 : 0.5,
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ fontWeight: '500' }}>
                      Step {stepNum} {isCompleted ? '✓' : isCurrent ? '→' : '○'}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                      {getStepTitle(stepNum)}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Content Area */}
            <div style={{ flex: 1, minWidth: 0 }}>
              {renderStepContent(selectedStory, currentStep)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;