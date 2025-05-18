import { TeamMember, EventTeamMember } from '../types';
import { apiClient } from '@/shared/services/apiClient';

export const teamService = {
  // Banco de Talentos (independente de eventos)
  getAllMembers: async (): Promise<TeamMember[]> => {
    const response = await apiClient.get('/team-members');
    return response.data;
  },

  createMember: async (data: Omit<TeamMember, 'id'>): Promise<TeamMember> => {
    const response = await apiClient.post('/team-members', data);
    return response.data;
  },

  // Membros associados a um evento específico
  getEventTeam: async (eventId: string): Promise<EventTeamMember[]> => {
    const response = await apiClient.get(`/events/${eventId}/team`);
    return response.data;
  },

  addMemberToEvent: async (
    eventId: string, 
    memberId: string, 
    role?: string
  ): Promise<EventTeamMember> => {
    const response = await apiClient.post(`/events/${eventId}/team`, {
      memberId,
      role
    });
    return response.data;
  },

  updateMemberRole: async (
    eventId: string, 
    memberId: string, 
    role: string
  ): Promise<EventTeamMember> => {
    const response = await apiClient.patch(
      `/events/${eventId}/team/${memberId}`, 
      { role }
    );
    return response.data;
  },

  removeMemberFromEvent: async (
    eventId: string, 
    memberId: string
  ): Promise<void> => {
    await apiClient.delete(`/events/${eventId}/team/${memberId}`);
  }
};