import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  currentStoryId: string | null;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  
  setCurrentStory: (id: string | null) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentStoryId: null,
      sidebarCollapsed: false,
      theme: 'light',
      
      setCurrentStory: (id) => set({ currentStoryId: id }),
      
      toggleSidebar: () => 
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      setSidebarCollapsed: (collapsed) => 
        set({ sidebarCollapsed: collapsed }),
      
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'snowmeth-app-storage',
      partialize: (state) => ({
        currentStoryId: state.currentStoryId,
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);