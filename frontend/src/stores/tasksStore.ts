import { create } from 'zustand';
import { TaskStatusResponse } from '../types';

interface TasksState {
  activeTasks: Map<string, TaskStatusResponse>;
  taskHistory: TaskStatusResponse[];
  
  addTask: (task: TaskStatusResponse) => void;
  updateTask: (taskId: string, update: Partial<TaskStatusResponse>) => void;
  removeTask: (taskId: string) => void;
  clearHistory: () => void;
}

export const useTasksStore = create<TasksState>((set, get) => ({
  activeTasks: new Map(),
  taskHistory: [],
  
  addTask: (task) =>
    set((state) => {
      const newActiveTasks = new Map(state.activeTasks);
      newActiveTasks.set(task.task_id, task);
      return { activeTasks: newActiveTasks };
    }),
  
  updateTask: (taskId, update) =>
    set((state) => {
      const newActiveTasks = new Map(state.activeTasks);
      const existingTask = newActiveTasks.get(taskId);
      
      if (existingTask) {
        const updatedTask = { ...existingTask, ...update };
        newActiveTasks.set(taskId, updatedTask);
        
        // Move completed/failed tasks to history
        if (updatedTask.status === 'completed' || updatedTask.status === 'failed') {
          const newHistory = [...state.taskHistory, updatedTask];
          // Keep only last 10 tasks in history
          if (newHistory.length > 10) {
            newHistory.shift();
          }
          
          return {
            activeTasks: newActiveTasks,
            taskHistory: newHistory,
          };
        }
      }
      
      return { activeTasks: newActiveTasks };
    }),
  
  removeTask: (taskId) =>
    set((state) => {
      const newActiveTasks = new Map(state.activeTasks);
      newActiveTasks.delete(taskId);
      return { activeTasks: newActiveTasks };
    }),
  
  clearHistory: () => set({ taskHistory: [] }),
}));