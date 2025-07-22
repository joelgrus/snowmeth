import React, { useState, useEffect, useRef } from 'react';
import styles from '../styles/components.module.css';
import { GeneratingIndicator } from './GeneratingIndicator';

interface Chapter {
  chapterNumber: number;
  title: string;
  content: string;
  wordCount: number;
  generatedAt?: string;
}

interface NovelWriterEditorProps {
  storyId: string;
  storySlug: string;
  scenes: any; // Scene data from step 9
  existingChapters?: any; // Existing chapter data from story
  onStoryUpdate?: (updatedStory: any) => void; // Callback to update parent story state
}

export const NovelWriterEditor: React.FC<NovelWriterEditorProps> = ({ storyId, storySlug, scenes, existingChapters, onStoryUpdate }) => {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatingChapter, setGeneratingChapter] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPdfExport, setShowPdfExport] = useState(false);
  const [writingStyle, setWritingStyle] = useState<string>('');
  const [showStyleInput, setShowStyleInput] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [showRefineInput, setShowRefineInput] = useState(false);
  const [refineInstructions, setRefineInstructions] = useState('');
  const chapterViewerRef = useRef<HTMLDivElement>(null);

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
            generatedAt: existingChapter?.generated_at
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
            generatedAt: existingChapter?.generated_at
          });
        });
      }
      
      setChapters(chapterList);
    } catch (err) {
      console.error('Error parsing scenes:', err);
    }
  }, [scenes, existingChapters]);

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
      
      // Clear existing content for this chapter
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { ...ch, content: '', wordCount: 0, generatedAt: undefined }
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
                // Update chapter content in real-time
                setChapters(prev => prev.map(ch => 
                  ch.chapterNumber === chapterNumber 
                    ? { 
                        ...ch, 
                        content: fullContent,
                        wordCount: fullContent.split(' ').length,
                        generatedAt: new Date().toISOString()
                      }
                    : ch
                ));
              } else if (data.type === 'complete') {
                wordCount = data.word_count;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      // Final update with correct word count
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { 
              ...ch, 
              content: fullContent, 
              wordCount: wordCount || fullContent.split(' ').length,
              generatedAt: new Date().toISOString()
            }
          : ch
      ));
      
      // Scroll to top of chapter viewer after a brief delay to ensure content is rendered
      setTimeout(scrollChapterViewerToTop, 100);

      // Update parent story state with latest data
      if (onStoryUpdate) {
        try {
          const storyResponse = await fetch(`/api/stories/${storyId}`);
          if (storyResponse.ok) {
            const updatedStory = await storyResponse.json();
            onStoryUpdate(updatedStory);
          }
        } catch (err) {
          console.error('Failed to refresh story data:', err);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate chapter');
    } finally {
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

      // Clear existing content for this chapter before streaming
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { ...ch, content: '', wordCount: 0, generatedAt: undefined }
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
                // Update chapter content in real-time
                setChapters(prev => prev.map(ch => 
                  ch.chapterNumber === chapterNumber 
                    ? { 
                        ...ch, 
                        content: fullContent,
                        wordCount: fullContent.split(' ').length,
                        generatedAt: new Date().toISOString()
                      }
                    : ch
                ));
              } else if (data.type === 'complete') {
                wordCount = data.word_count;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }

      // Final update with correct word count
      setChapters(prev => prev.map(ch => 
        ch.chapterNumber === chapterNumber 
          ? { 
              ...ch, 
              content: fullContent, 
              wordCount: wordCount || fullContent.split(' ').length,
              generatedAt: new Date().toISOString()
            }
          : ch
      ));
      
      setShowRefineInput(false);
      setRefineInstructions('');

      // Update parent story state with latest data
      if (onStoryUpdate) {
        try {
          const storyResponse = await fetch(`/api/stories/${storyId}`);
          if (storyResponse.ok) {
            const updatedStory = await storyResponse.json();
            onStoryUpdate(updatedStory);
          }
        } catch (err) {
          console.error('Failed to refresh story data:', err);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refine chapter');
    } finally {
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
        <button
          className={styles.toggleButton}
          onClick={() => setShowStyleInput(!showStyleInput)}
        >
          ✏️ Writing Style {showStyleInput ? '▼' : '▶'}
        </button>
        {showStyleInput && (
          <div className={styles.styleInputContainer}>
            <label htmlFor="writing-style">Writing Instructions (applied to all chapters):</label>
            <textarea
              id="writing-style"
              className={styles.styleTextarea}
              value={writingStyle}
              onChange={(e) => setWritingStyle(e.target.value)}
              placeholder="e.g. 'Use humor and wit throughout', 'Write in vernacular/dialect', 'Focus on atmospheric descriptions', 'Keep dialogue snappy and modern'..."
              rows={3}
            />
          </div>
        )}
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
                {!chapter.content && generatingChapter !== chapter.chapterNumber && canGenerate && (
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
                {generatingChapter === chapter.chapterNumber && (
                  <GeneratingIndicator />
                )}
              </div>
            );
          })}
        </div>

        <div className={styles.chapterViewer} ref={chapterViewerRef}>
          {selectedChapter && chapters[selectedChapter - 1]?.content ? (
            <>
              <div className={styles.chapterViewerHeader}>
                <h4>{chapters[selectedChapter - 1].title}</h4>
                <div className={styles.chapterActions}>
                  {canRefineChapter(selectedChapter) && (
                    <button
                      className={styles.refineButton}
                      onClick={() => setShowRefineInput(!showRefineInput)}
                      disabled={isGenerating || isRefining}
                    >
                      ✨ Refine
                    </button>
                  )}
                  <button
                    className={styles.regenerateButton}
                    onClick={() => handleRegenerateChapter(selectedChapter)}
                    disabled={isGenerating || isRefining}
                  >
                    🔄 Regenerate
                  </button>
                </div>
              </div>
              
              {showRefineInput && selectedChapter && canRefineChapter(selectedChapter) && (
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
              <div className={styles.chapterContent}>
                {chapters[selectedChapter - 1].content}
              </div>
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