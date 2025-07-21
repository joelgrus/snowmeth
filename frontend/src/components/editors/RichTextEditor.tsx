import React, { useState, useEffect } from 'react';
import { useAutoSave } from '../../hooks/useAutoSave';

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  onSave?: (content: string) => void;
  placeholder?: string;
  isLoading?: boolean;
  minHeight?: number;
}

export function RichTextEditor({
  content = '',
  onChange,
  onSave,
  placeholder = "Start writing...",
  isLoading = false,
  minHeight = 300,
}: RichTextEditorProps) {
  const [value, setValue] = useState(content);

  // Auto-save functionality
  const { isSaving, lastSaved, isDirty, error, markDirty, saveNow } = useAutoSave(
    value,
    async (data) => {
      if (onSave) {
        await onSave(data);
      }
    }
  );

  // Update local state when content prop changes
  useEffect(() => {
    setValue(content);
  }, [content]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    onChange(newValue);
    markDirty();
  };

  const wordCount = value.trim().split(/\s+/).filter(word => word.length > 0).length;
  const charCount = value.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Editor Toolbar */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        padding: '8px 12px',
        backgroundColor: '#f5f5f5',
        borderRadius: '6px',
        fontSize: '14px'
      }}>
        <div style={{ color: '#666' }}>
          Rich text editor (for longer content)
        </div>
        <div style={{ display: 'flex', gap: '16px', color: '#666' }}>
          <span>{wordCount} words</span>
          <span>{charCount} characters</span>
        </div>
      </div>

      {/* Main Editor */}
      <div style={{ position: 'relative' }}>
        <textarea
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={isLoading}
          style={{
            width: '100%',
            minHeight: `${minHeight}px`,
            padding: '16px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontSize: '16px',
            lineHeight: '1.6',
            resize: 'vertical',
            fontFamily: 'Georgia, "Times New Roman", serif',
            outline: 'none',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => {
            e.target.style.borderColor = '#2196f3';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = '#ddd';
          }}
        />
      </div>

      {/* Writing Tips */}
      <div style={{
        padding: '12px',
        backgroundColor: '#e3f2fd',
        borderRadius: '6px',
        fontSize: '14px',
        color: '#1976d2'
      }}>
        <strong>💡 Writing Tips:</strong>
        <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px' }}>
          <li>Write in present tense for immediate impact</li>
          <li>Focus on conflict and character motivation</li>
          <li>Keep paragraphs concise and engaging</li>
          <li>Show, don't tell - use specific details</li>
        </ul>
      </div>

      {/* Save Status */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        fontSize: '14px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {isSaving && (
            <span style={{ color: '#2196f3' }}>Saving...</span>
          )}
          {lastSaved && !isSaving && !isDirty && (
            <span style={{ color: '#4caf50' }}>
              Saved {lastSaved.toLocaleTimeString()}
            </span>
          )}
          {isDirty && !isSaving && (
            <span style={{ color: '#ff9800' }}>Unsaved changes</span>
          )}
          {error && (
            <span style={{ color: '#f44336' }}>Error: {error}</span>
          )}
        </div>
        
        {isDirty && (
          <button
            onClick={saveNow}
            disabled={isSaving}
            style={{
              padding: '6px 12px',
              backgroundColor: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Save Now
          </button>
        )}
      </div>
    </div>
  );
}