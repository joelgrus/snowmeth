import React, { useState, useEffect } from 'react';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';
import { useAutoSave } from '../../hooks/useAutoSave';
import { EditorProps } from '../../types';

interface SimpleTextEditorProps extends EditorProps<string> {
  placeholder?: string;
  maxLength?: number;
  showCharCount?: boolean;
}

export function SimpleTextEditor({
  content = '',
  onChange,
  onSave,
  placeholder,
  maxLength,
  showCharCount = true,
  isLoading = false,
}: SimpleTextEditorProps) {
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

  const handleManualSave = async () => {
    try {
      await saveNow();
    } catch (err) {
      console.error('Manual save failed:', err);
    }
  };

  return (
    <div className="space-y-4">
      <Textarea
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        maxLength={maxLength}
        showCharCount={showCharCount}
        className="min-h-32"
        disabled={isLoading}
      />
      
      {/* Save Status */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          {isSaving && (
            <span className="text-blue-600">Saving...</span>
          )}
          {lastSaved && !isSaving && !isDirty && (
            <span className="text-green-600">
              Saved {lastSaved.toLocaleTimeString()}
            </span>
          )}
          {isDirty && !isSaving && (
            <span className="text-yellow-600">Unsaved changes</span>
          )}
          {error && (
            <span className="text-red-600">Error: {error}</span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {isDirty && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleManualSave}
              isLoading={isSaving}
            >
              Save Now
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}