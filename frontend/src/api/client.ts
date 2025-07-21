import { io, Socket } from 'socket.io-client';
import {
  Story,
  StoryCreateRequest,
  StoryListResponse,
  StoryDetailResponse,
  TaskResponse,
  TaskStatusResponse,
  RefineRequest,
} from '../types/api';

class SnowmethApiClient {
  private baseURL: string;
  private socket: Socket | null = null;

  constructor(baseURL: string = '') {
    // Use empty string for relative URLs when using Vite proxy
    this.baseURL = baseURL;
  }

  // Initialize WebSocket connection
  initializeSocket() {
    if (!this.socket) {
      this.socket = io(this.baseURL);
    }
    return this.socket;
  }

  // Story operations
  async createStory(data: StoryCreateRequest): Promise<TaskResponse> {
    const response = await fetch(`${this.baseURL}/api/stories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getStory(id: string): Promise<StoryDetailResponse> {
    const response = await fetch(`${this.baseURL}/api/stories/${id}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async listStories(): Promise<StoryListResponse> {
    const response = await fetch(`${this.baseURL}/api/stories`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteStory(id: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/stories/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }

  // Story progression operations
  async advanceStory(id: string): Promise<TaskResponse> {
    const response = await fetch(`${this.baseURL}/api/stories/${id}/next`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async refineStory(id: string, instructions: string): Promise<TaskResponse> {
    const response = await fetch(`${this.baseURL}/api/stories/${id}/refine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ instructions }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async analyzeStory(id: string): Promise<TaskResponse> {
    const response = await fetch(`${this.baseURL}/api/stories/${id}/analyze`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Task operations
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await fetch(`${this.baseURL}/api/tasks/${taskId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Real-time task updates
  subscribeToTask(taskId: string, callback: (status: TaskStatusResponse) => void) {
    if (!this.socket) {
      this.initializeSocket();
    }

    this.socket?.on(`task:${taskId}`, callback);
  }

  unsubscribeFromTask(taskId: string) {
    this.socket?.off(`task:${taskId}`);
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const apiClient = new SnowmethApiClient();
export default apiClient;