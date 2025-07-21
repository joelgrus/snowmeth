import { useCallback, useEffect } from 'react';
import { useTasksStore } from '../stores/tasksStore';
import { apiClient } from '../api/client';
import { TaskResponse, TaskStatusResponse } from '../types';

export function useTaskManager() {
  const { activeTasks, addTask, updateTask, removeTask } = useTasksStore();

  // Initialize WebSocket connection
  useEffect(() => {
    apiClient.initializeSocket();
    
    return () => {
      apiClient.disconnect();
    };
  }, []);

  const startTask = useCallback(async (taskPromise: Promise<TaskResponse>) => {
    try {
      const taskResponse = await taskPromise;
      const task: TaskStatusResponse = {
        task_id: taskResponse.task_id,
        status: 'pending',
        progress: 0,
      };
      
      addTask(task);
      
      // Subscribe to real-time updates
      apiClient.subscribeToTask(task.task_id, (update: TaskStatusResponse) => {
        updateTask(task.task_id, update);
        
        // Auto-remove completed/failed tasks after 5 seconds
        if (update.status === 'completed' || update.status === 'failed') {
          setTimeout(() => removeTask(task.task_id), 5000);
        }
      });
      
      return task.task_id;
    } catch (error) {
      console.error('Failed to start task:', error);
      throw error;
    }
  }, [addTask, updateTask, removeTask]);

  const cancelTask = useCallback((taskId: string) => {
    apiClient.unsubscribeFromTask(taskId);
    removeTask(taskId);
  }, [removeTask]);

  return {
    activeTasks: Array.from(activeTasks.values()),
    startTask,
    cancelTask,
  };
}