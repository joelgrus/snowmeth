import React, { useState, useEffect } from 'react';
import { useAutoSave } from '../../hooks/useAutoSave';

interface Character {
  name: string;
  description: string;
}

interface CharacterListEditorProps {
  content: Character[];
  onChange: (characters: Character[]) => void;
  onSave?: (characters: Character[]) => void;
  isLoading?: boolean;
}

export function CharacterListEditor({
  content = [],
  onChange,
  onSave,
  isLoading = false,
}: CharacterListEditorProps) {
  const [characters, setCharacters] = useState<Character[]>(content);

  // Auto-save functionality
  const { isSaving, lastSaved, isDirty, error, markDirty, saveNow } = useAutoSave(
    characters,
    async (data) => {
      if (onSave) {
        await onSave(data);
      }
    }
  );

  // Update local state when content prop changes
  useEffect(() => {
    setCharacters(content);
  }, [content]);

  const handleCharactersChange = (newCharacters: Character[]) => {
    setCharacters(newCharacters);
    onChange(newCharacters);
    markDirty();
  };

  const addCharacter = () => {
    const newCharacters = [...characters, { name: '', description: '' }];
    handleCharactersChange(newCharacters);
  };

  const removeCharacter = (index: number) => {
    const newCharacters = characters.filter((_, i) => i !== index);
    handleCharactersChange(newCharacters);
  };

  const updateCharacter = (index: number, field: keyof Character, value: string) => {
    const newCharacters = [...characters];
    newCharacters[index] = { ...newCharacters[index], [field]: value };
    handleCharactersChange(newCharacters);
  };

  return (
    <div style={{ space: '16px' }}>
      <div style={{ marginBottom: '16px' }}>
        <p style={{ color: '#666', fontSize: '14px', margin: '0 0 16px 0' }}>
          List your main characters with brief descriptions. You can reorder them by importance.
        </p>
        <button
          onClick={addCharacter}
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          + Add Character
        </button>
      </div>

      {/* Character List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {characters.map((character, index) => (
          <div
            key={index}
            style={{
              padding: '16px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: '#fff'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ 
                minWidth: '80px', 
                fontWeight: 'bold', 
                color: '#666',
                fontSize: '14px'
              }}>
                Character {index + 1}
              </span>
              <button
                onClick={() => removeCharacter(index)}
                disabled={isLoading}
                style={{
                  marginLeft: 'auto',
                  padding: '4px 8px',
                  backgroundColor: '#f44336',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                Remove
              </button>
            </div>
            
            <div style={{ marginBottom: '12px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '4px', 
                fontWeight: '500',
                fontSize: '14px'
              }}>
                Name
              </label>
              <input
                type="text"
                value={character.name}
                onChange={(e) => updateCharacter(index, 'name', e.target.value)}
                placeholder="Character name"
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '4px', 
                fontWeight: '500',
                fontSize: '14px'
              }}>
                Description
              </label>
              <textarea
                value={character.description}
                onChange={(e) => updateCharacter(index, 'description', e.target.value)}
                placeholder="Brief character description..."
                disabled={isLoading}
                rows={3}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  resize: 'vertical'
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {characters.length === 0 && (
        <div style={{
          padding: '32px',
          textAlign: 'center',
          color: '#999',
          border: '2px dashed #ddd',
          borderRadius: '8px'
        }}>
          <p>No characters yet. Click "Add Character" to get started!</p>
          <p style={{ fontSize: '12px' }}>
            Tip: Start with your protagonist, then add antagonist and key supporting characters.
          </p>
        </div>
      )}

      {/* Save Status */}
      <div style={{ 
        marginTop: '16px',
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
          
          <span style={{ color: '#666' }}>
            {characters.length} character{characters.length !== 1 ? 's' : ''}
          </span>
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