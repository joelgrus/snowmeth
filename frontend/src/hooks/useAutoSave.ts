import { useState, useEffect, useMemo, useCallback } from 'react';

function debounce<T extends any[]>(
  func: (...args: T) => Promise<void>,
  delay: number
): (...args: T) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: T) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

export function useAutoSave<T>(
  data: T,
  saveFunction: (data: T) => Promise<void>,
  delay: number = 2000
) {
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const debouncedSave = useMemo(
    () => debounce(async (dataToSave: T) => {
      setIsSaving(true);
      setError(null);
      
      try {
        await saveFunction(dataToSave);
        setLastSaved(new Date());
        setIsDirty(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Save failed');
        console.error('Auto-save failed:', err);
      } finally {
        setIsSaving(false);
      }
    }, delay),
    [saveFunction, delay]
  );

  useEffect(() => {
    if (isDirty && data !== undefined && data !== null) {
      debouncedSave(data);
    }
  }, [data, isDirty, debouncedSave]);

  const markDirty = useCallback(() => {
    setIsDirty(true);
    setError(null);
  }, []);

  const saveNow = useCallback(async () => {
    if (data !== undefined && data !== null) {
      setIsSaving(true);
      setError(null);
      
      try {
        await saveFunction(data);
        setLastSaved(new Date());
        setIsDirty(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Save failed');
        throw err;
      } finally {
        setIsSaving(false);
      }
    }
  }, [data, saveFunction]);

  return { 
    isSaving, 
    lastSaved, 
    isDirty,
    error,
    markDirty,
    saveNow,
  };
}