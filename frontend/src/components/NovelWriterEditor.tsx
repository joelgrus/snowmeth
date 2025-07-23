import React, { useState, useEffect, useRef } from 'react';
import styles from '../styles/components.module.css';
import { GeneratingIndicator } from './GeneratingIndicator';

interface Chapter {
  chapterNumber: number;
  title: string;
  content: string;
  wordCount: number;
  generatedAt?: string;
  isGenerating?: boolean;
}

import type { Story } from '../types/simple';

interface NovelWriterEditorProps {
  story: Story;
  onStoryUpdate?: (updatedStory: any) => void;
  writingStyle: string;
  onWritingStyleChange: (style: string) => void;
}

export const NovelWriterEditor: React.FC<NovelWriterEditorProps> = ({ story, onStoryUpdate, writingStyle, onWritingStyleChange }) => {
  const { story_id: storyId, slug: storySlug, steps, chapters: existingChapters } = story;
  const scenes = steps['9'];

  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatingChapter, setGeneratingChapter] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPdfExport, setShowPdfExport] = useState(false);
  // Writing style is always visible
  const [isRefining, setIsRefining] = useState(false);
  const [showRefineInput, setShowRefineInput] = useState(false);
  const [refineInstructions, setRefineInstructions] = useState('');
  const chapterViewerRef = useRef<HTMLDivElement>(null);
  const [typewriterBuffer, setTypewriterBuffer] = useState<string>('');
  const [displayedContent, setDisplayedContent] = useState<string>('');
  const typewriterTimerRef = useRef<NodeJS.Timeout | null>(null);


  // Parse scenes data to determine chapters
  useEffect(() => {
    try {
      const sceneData = typeof scenes === 'string' ? JSON.parse(scenes) : scenes;
      const chapterList: Chapter[] = [];
      
      // Convert scenes to chapters
      if (Array.isArray(sceneData)) {
        sceneData.forEach((scene, index) => {
          const chapterNum = index + 1;
          const existingChapter = existingChapters?.[chapterNum];
          
          chapterList.push({
            chapterNumber: chapterNum,
            title: scene.title || `Chapter ${chapterNum}`,
            content: existingChapter?.content || '',
            wordCount: existingChapter?.word_count || 0,
            generatedAt: existingChapter?.generated_at,
            isGenerating: false
          });
        });
      } else if (typeof sceneData === 'object') {
        Object.entries(sceneData).forEach(([key, scene]: [string, any], index) => {
          const chapterNum = scene.scene_number || index + 1;
          const existingChapter = existingChapters?.[chapterNum];
          
          chapterList.push({
            chapterNumber: chapterNum,
            title: scene.title || `Chapter ${chapterNum}`,
            content: existingChapter?.content || '',
            wordCount: existingChapter?.word_count || 0,
            generatedAt: existingChapter?.generated_at,
            isGenerating: false
          });
        });
      }
      
      setChapters(chapterList);
    } catch (err) {
      console.error('Error parsing scenes:', err);
    }
  }, [scenes, existingChapters]);

  // Typewriter effect - display characters one by one with delay
  useEffect(() => {
    if (typewriterBuffer.length > displayedContent.length) {
      if (typewriterTimerRef.current) {
        clearTimeout(typewriterTimerRef.current);
      }
      
      typewriterTimerRef.current = setTimeout(() => {
        setDisplayedContent(prev => {
          const newContent = typewriterBuffer.slice(0, prev.length + 1);
          
          // Auto-scroll to keep cursor visible only during generation
          setTimeout(() => {
            if (chapterViewerRef.current && newContent.length < typewriterBuffer.length) {
              chapterViewerRef.current.scrollTop = chapterViewerRef.current.scrollHeight;
            }
          }, 0);
          
          // Check if we've finished typing everything
          if (newContent.length >= typewriterBuffer.length && typewriterBuffer.length > 0) {
            // Mark generation as complete
            setTimeout(() => {
              const finalChapters = chapters.map(ch => 
                ch.isGenerating 
                  ? { 
                      ...ch, 
                      content: typewriterBuffer,
                      wordCount: typewriterBuffer.split(' ').length,
                      generatedAt: new Date().toISOString(),
                      isGenerating: false
                    }
                  : ch
              );
              setChapters(finalChapters);

              // Also clear global generating state
              setIsGenerating(false);
              setGeneratingChapter(null);
              setIsRefining(false);

              // IMPORTANT: Update the parent component with the new chapter data
              // Use a functional update to avoid stale state
              if (onStoryUpdate) {
                const updatedChaptersData = finalChapters.reduce((acc, ch) => {
                  if (ch.content) {
                    acc[ch.chapterNumber] = {
                      content: ch.content,
                      word_count: ch.wordCount,
                      generated_at: ch.generatedAt,
                      scene_title: ch.title,
                    };
                  }
                  return acc;
                }, {} as any);

                onStoryUpdate((prevStory: Story) => ({
                  ...prevStory,
                  chapters: updatedChaptersData,
                }));
              }
            }, 100);
          }
          
          return newContent;
        });
      }, 0); // No delay - type as fast as possible
    }
    
    return () => {
      if (typewriterTimerRef.current) {
        clearTimeout(typewriterTimerRef.current);
      }
    };
  }, [typewriterBuffer, displayedContent, story, onStoryUpdate, chapters]);

  const scrollChapterViewerToTop = () => {
    if (chapterViewerRef.current) {
      chapterViewerRef.current.scrollTop = 0;
    }
  };

  const handleGenerateChapter = async (chapterNumber: number) => {
    setIsGenerating(true);
    setGeneratingChapter(chapterNumber);
    setError(null);

    try {
      const response = await fetch(`/api/stories/${storyId}/generate_chapter/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          chapter_number: chapterNumber,
          writing_style: writingStyle || undefined
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate chapter');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let wordCount = 0;

      // Select the chapter immediately so streaming content is visible
      setSelectedChapter(chapterNumber);
      
      // Clear existing content for this chapter and mark it as being generated
      // Also reset typewriter state
      setTypewriterBuffer('');
      setDisplayedContent('');
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { ...ch, content: '', wordCount: 0, generatedAt: undefined, isGenerating: true }
          : ch
      ));

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines[lines.length - 1]; // Keep incomplete line in buffer
        
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                throw new Error(data.error);
              }
              
              if (data.type === 'content') {
                fullContent += data.content;
                // Update typewriter buffer for character-by-character display
                setTypewriterBuffer(fullContent);
              } else if (data.type === 'complete') {
                wordCount = data.word_count;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      // Don't finish generation immediately - let typewriter complete naturally
      // The generation will be marked complete when typewriter catches up

      // Don't update parent story state during generation - it resets our isGenerating state
      // This will be handled when typewriter completes
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate chapter');
      // Only stop generating on error, otherwise let typewriter finish naturally
      setIsGenerating(false);
      setGeneratingChapter(null);
    }
  };

  const handleRegenerateChapter = async (chapterNumber: number) => {
    const hasLaterChapters = chapters.some(ch => ch.chapterNumber > chapterNumber && ch.content);
    const confirmMessage = hasLaterChapters 
      ? 'Are you sure you want to regenerate this chapter? This will also delete all chapters after it since they depend on this content.'
      : 'Are you sure you want to regenerate this chapter? The current content will be replaced.';
      
    if (window.confirm(confirmMessage)) {
      // First, clear any chapters after this one
      if (hasLaterChapters) {
        setChapters(prev => prev.map(ch => 
          ch.chapterNumber > chapterNumber 
            ? { ...ch, content: '', wordCount: 0, generatedAt: undefined }
            : ch
        ));
      }
      
      await handleGenerateChapter(chapterNumber);
    }
  };

  const handleExportNovel = async () => {
    try {
      const response = await fetch(`/api/stories/${storyId}/export_novel`);
      
      if (!response.ok) {
        throw new Error('Failed to export novel');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${storySlug.replace(/[^a-zA-Z0-9]/g, '_')}_novel.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export novel');
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await fetch(`/api/stories/${storyId}/export_pdf`);
      
      if (!response.ok) {
        throw new Error('Failed to export PDF');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `snowflake_method_${storySlug.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export PDF');
    }
  };

  const handleRefineChapter = async (chapterNumber: number, instructions: string) => {
    setIsRefining(true);
    setError(null);

    try {
      const response = await fetch(`/api/stories/${storyId}/refine_chapter/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          chapter_number: chapterNumber,
          instructions: instructions
        })
      });

      if (!response.ok) {
        throw new Error('Failed to refine chapter');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let wordCount = 0;

      // Clear existing content for this chapter before streaming and mark as generating
      // Also reset typewriter state for refinement
      setTypewriterBuffer('');
      setDisplayedContent('');
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { ...ch, content: '', wordCount: 0, generatedAt: undefined, isGenerating: true }
          : ch
      ));

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines[lines.length - 1]; // Keep incomplete line in buffer
        
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                throw new Error(data.error);
              }
              
              if (data.type === 'content') {
                fullContent += data.content;
                // Update typewriter buffer for character-by-character display
                setTypewriterBuffer(fullContent);
              } else if (data.type === 'complete') {
                wordCount = data.word_count;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      // Don't finish refinement immediately - let typewriter complete naturally
      // The refinement will be marked complete when typewriter catches up
      
      setShowRefineInput(false);
      setRefineInstructions('');

      // Don't update parent story state during refinement - it resets our isGenerating state
      // This will be handled when typewriter completes
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refine chapter');
      // Only stop refining on error, otherwise let typewriter finish naturally
      setIsRefining(false);
    }
  };

  const totalWordCount = chapters.reduce((sum, ch) => sum + ch.wordCount, 0);
  const completedChapters = chapters.filter(ch => ch.content).length;
  
  // Determine which chapters can be generated
  const getNextChapterToGenerate = () => {
    for (let i = 0; i < chapters.length; i++) {
      if (!chapters[i].content) {
        return chapters[i].chapterNumber;
      }
    }
    return null;
  };
  
  const canGenerateChapter = (chapterNumber: number) => {
    // Chapter 1 can always be generated
    if (chapterNumber === 1) return true;
    
    // Other chapters can only be generated if all previous chapters exist
    return chapters
      .filter(ch => ch.chapterNumber < chapterNumber)
      .every(ch => ch.content);
  };
  
  const nextChapterToGenerate = getNextChapterToGenerate();
  
  // Determine if a chapter can be refined (only the most recent completed chapter)
  const canRefineChapter = (chapterNumber: number) => {
    if (!chapters[chapterNumber - 1]?.content) return false; // Must have content
    
    // Find the highest numbered chapter with content
    const lastCompletedChapter = chapters
      .filter(ch => ch.content)
      .reduce((max, ch) => ch.chapterNumber > max ? ch.chapterNumber : max, 0);
    
    return chapterNumber === lastCompletedChapter;
  };

  return (
    <div className={styles.novelWriterContainer}>
      <div className={styles.novelWriterHeader}>
        <h3>Write Your Novel</h3>
        <div className={styles.novelWriterStats}>
          <span>Progress: {completedChapters} / {chapters.length} chapters</span>
          <span>Total Words: {totalWordCount.toLocaleString()}</span>
        </div>
      </div>

      <div className={styles.writingStyleSection}>
        <div className={styles.styleInputContainer}>
          <label htmlFor="writing-style">Writing Instructions (applied to all chapters):</label>
          <textarea
            id="writing-style"
            className={styles.styleTextarea}
            value={writingStyle}
            onChange={(e) => onWritingStyleChange(e.target.value)}
            placeholder="e.g. 'Use humor and wit throughout', 'Write in vernacular/dialect', 'Focus on atmospheric descriptions', 'Keep dialogue snappy and modern'..."
            rows={3}
          />
        </div>
      </div>

      <div className={styles.novelWriterContent}>
        <div className={styles.chapterList}>
          <h4>Chapters</h4>
          {chapters.map(chapter => {
            const canGenerate = canGenerateChapter(chapter.chapterNumber);
            const isNextToGenerate = chapter.chapterNumber === nextChapterToGenerate;
            
            return (
              <div 
                key={chapter.chapterNumber}
                className={`${styles.chapterItem} ${
                  selectedChapter === chapter.chapterNumber ? styles.selected : ''
                } ${chapter.content ? styles.completed : ''} ${
                  !canGenerate ? styles.disabled : ''
                }`}
                onClick={() => {
                  setSelectedChapter(chapter.chapterNumber);
                  setTimeout(scrollChapterViewerToTop, 100);
                }}
              >
                <div className={styles.chapterInfo}>
                  <strong>
                    {chapter.title}
                    {isNextToGenerate && !chapter.content && (
                      <span className={styles.nextIndicator}> (Next)</span>
                    )}
                  </strong>
                  {chapter.content && (
                    <span className={styles.wordCount}>
                      {chapter.wordCount.toLocaleString()} words
                    </span>
                  )}
                  {!canGenerate && !chapter.content && (
                    <span className={styles.blockedText}>Complete previous chapters first</span>
                  )}
                </div>
                {!chapter.content && !chapter.isGenerating && canGenerate && (
                  <button
                    className={styles.generateButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateChapter(chapter.chapterNumber);
                    }}
                    disabled={isGenerating}
                  >
                    ✨ Generate
                  </button>
                )}
                {chapter.isGenerating && (
                  <div className={styles.generatingChapterIndicator}>
                    <span>🤖 Generating...</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className={styles.chapterViewer} ref={chapterViewerRef}>
          {selectedChapter && (chapters[selectedChapter - 1]?.content || chapters[selectedChapter - 1]?.isGenerating) ? (
            <>
              <div className={styles.chapterViewerHeader}>
                <h4>{chapters[selectedChapter - 1].title}</h4>
                <div className={styles.chapterActions}>
                  {canRefineChapter(selectedChapter) && !chapters[selectedChapter - 1]?.isGenerating && (
                    <button
                      className={styles.refineButton}
                      onClick={() => setShowRefineInput(!showRefineInput)}
                      disabled={isGenerating || isRefining}
                    >
                      ✨ Refine
                    </button>
                  )}
                  {!chapters[selectedChapter - 1]?.isGenerating && (
                    <button
                      className={styles.regenerateButton}
                      onClick={() => handleRegenerateChapter(selectedChapter)}
                      disabled={isGenerating || isRefining}
                    >
                      🔄 Regenerate
                    </button>
                  )}
                </div>
              </div>
              
              {showRefineInput && selectedChapter && canRefineChapter(selectedChapter) && !chapters[selectedChapter - 1]?.isGenerating && (
                <div className={styles.refineInputSection}>
                  <label htmlFor="refine-instructions">
                    Refine this chapter:
                  </label>
                  <textarea
                    id="refine-instructions"
                    className={styles.refineTextarea}
                    value={refineInstructions}
                    onChange={(e) => setRefineInstructions(e.target.value)}
                    placeholder="e.g., 'Add more dialogue', 'Increase tension in the middle section', 'Make the ending more dramatic'..."
                    rows={3}
                    disabled={isRefining}
                  />
                  <div className={styles.refineActions}>
                    <button
                      className={styles.refineSubmitButton}
                      onClick={() => handleRefineChapter(selectedChapter, refineInstructions)}
                      disabled={!refineInstructions.trim() || isRefining}
                    >
                      {isRefining ? '🔄 Refining...' : '✨ Apply Refinement'}
                    </button>
                    <button
                      className={styles.refineCancelButton}
                      onClick={() => {
                        setShowRefineInput(false);
                        setRefineInstructions('');
                      }}
                      disabled={isRefining}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              
              {chapters[selectedChapter - 1]?.isGenerating ? (
                <div className={styles.generatingIndicator}>
                  <div className={styles.generatingText}>🤖 Generating chapter...</div>
                  <div className={styles.typewriterContent}>
                    {displayedContent}
                    <span className={styles.cursor}>|</span>
                  </div>
                </div>
              ) : (
                <div className={styles.chapterContent}>
                  {chapters[selectedChapter - 1].content}
                </div>
              )}
            </>
          ) : selectedChapter ? (
            <div className={styles.chapterPlaceholder}>
              <p>This chapter hasn't been generated yet.</p>
              <button
                className={styles.generateButtonLarge}
                onClick={() => handleGenerateChapter(selectedChapter)}
                disabled={isGenerating}
              >
                ✨ Generate Chapter {selectedChapter}
              </button>
            </div>
          ) : (
            <div className={styles.chapterPlaceholder}>
              <p>Select a chapter from the list to view or generate its content.</p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className={styles.errorMessage}>
          ⚠️ {error}
        </div>
      )}

      <div className={styles.novelWriterActions}>
        <button
          className={styles.exportButton}
          onClick={handleExportNovel}
          disabled={completedChapters === 0}
        >
          📝 Export Novel (.txt)
        </button>
        <button
          className={styles.secondaryButton}
          onClick={() => setShowPdfExport(!showPdfExport)}
        >
          📄 Export Story Plan (PDF)
        </button>
      </div>

      {showPdfExport && (
        <div className={styles.pdfExportSection}>
          <h4>Export Story Plan</h4>
          <p>
            Export your complete Snowflake Method story plan as a PDF, including all 
            character descriptions, plot structure, and scene expansions.
          </p>
          <button
            className={styles.pdfExportButton}
            onClick={handleExportPDF}
          >
            📄 Download Story Plan PDF
          </button>
        </div>
      )}
    </div>
  );
};