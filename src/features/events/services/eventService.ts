import { Event, EventCreateData, EventUpdateData } from '../types';
import { apiClient } from '@/shared/services/apiClient';

export const eventService = {
  getAllEvents: async (): Promise<Event[]> => {
    const response = await apiClient.get('/events');
    return response.data;
  },

  getEvent: async (id: string): Promise<Event> => {
    const response = await apiClient.get(`/events/${id}`);
    return response.data;
  },

  createEvent: async (data: EventCreateData): Promise<Event> => {
    const response = await apiClient.post('/events', data);
    return response.data;
  },

  updateEvent: async (id: string, data: EventUpdateData): Promise<Event> => {
    const response = await apiClient.patch(`/events/${id}`, data);
    return response.data;
  },

  deleteEvent: async (id: string): Promise<void> => {
    await apiClient.delete(`/events/${id}`);
  }
};