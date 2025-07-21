import React, { useState } from 'react';
import styles from '../styles/components.module.css';

interface PDFExportEditorProps {
  storyId: string;
  storySlug: string;
}

export const PDFExportEditor: React.FC<PDFExportEditorProps> = ({ storyId, storySlug }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExportPDF = async () => {
    setIsExporting(true);
    setExportError(null);
    
    try {
      const response = await fetch(`/api/stories/${storyId}/export_pdf`);
      
      if (!response.ok) {
        throw new Error('Failed to export PDF');
      }
      
      // Get the PDF blob
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `snowflake_method_${storySlug.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('PDF export error:', error);
      setExportError(error instanceof Error ? error.message : 'Failed to export PDF');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className={styles.pdfExportContainer}>
      <div className={styles.pdfExportCard}>
        <div className={styles.pdfExportIcon}>📄</div>
        
        <div className={styles.pdfExportContent}>
          <h3 className={styles.pdfExportTitle}>Your Story Plan is Complete!</h3>
          <p className={styles.pdfExportDescription}>
            You've completed all 9 steps of the Snowflake Method. Your comprehensive story plan includes:
          </p>
          
          <ul className={styles.pdfExportFeatures}>
            <li>✓ One Sentence Summary</li>
            <li>✓ One Paragraph Summary</li>
            <li>✓ Character Summaries & Synopses</li>
            <li>✓ Story Structure & Plot</li>
            <li>✓ Detailed Story Synopsis</li>
            <li>✓ Character Charts</li>
            <li>✓ Scene List</li>
            <li>✓ Detailed Scene Expansions</li>
          </ul>
          
          <p className={styles.pdfExportSummary}>
            Export your complete story plan as a professionally formatted PDF document 
            that you can print, share, or reference while writing your first draft.
          </p>
        </div>
        
        <div className={styles.pdfExportActions}>
          {exportError && (
            <div className={styles.pdfExportError}>
              ⚠️ {exportError}
            </div>
          )}
          
          <button
            className={styles.pdfExportButton}
            onClick={handleExportPDF}
            disabled={isExporting}
          >
            {isExporting ? (
              <>
                <span className={styles.pdfExportSpinner}>⏳</span>
                Generating PDF...
              </>
            ) : (
              <>
                📄 Download PDF
              </>
            )}
          </button>
          
          <p className={styles.pdfExportHint}>
            The PDF will include all your completed steps in a clean, professional format.
          </p>
        </div>
      </div>
      
      <div className={styles.pdfExportNextSteps}>
        <h4 className={styles.pdfExportNextTitle}>Ready to Write?</h4>
        <p className={styles.pdfExportNextDescription}>
          With your Snowflake Method plan complete, you're ready to start writing your first draft! 
          Use your PDF as a reference guide to keep your story on track.
        </p>
        
        <div className={styles.pdfExportTips}>
          <div className={styles.pdfExportTip}>
            <strong>💡 Writing Tip:</strong> Don't worry about perfection in your first draft. 
            Focus on getting the story down following your plan.
          </div>
          <div className={styles.pdfExportTip}>
            <strong>📚 Reference:</strong> Keep your scene expansions handy - they're your 
            roadmap for each chapter or scene you write.
          </div>
        </div>
      </div>
    </div>
  );
};