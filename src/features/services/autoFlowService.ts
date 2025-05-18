import { briefingService } from '@/features/briefing/services/briefingService';
import { timelineService } from '@/features/timeline/services/timelineService';
import { deliveryService } from '@/features/deliveries/services/deliveryService';
import { teamService } from '@/features/team/services/teamService';

/**
 * Serviço que orquestra fluxos automáticos entre os módulos do sistema
 * baseados no princípio "Tudo nasce do evento. O resto é consequência."
 */
export const autoFlowService = {
  /**
   * Gera timeline automaticamente baseada no briefing e equipe
   */
  generateTimelineFromBriefing: async (eventId: string) => {
    // Obtém briefing e equipe
    const [briefing, team] = await Promise.all([
      briefingService.getEventBriefing(eventId),
      teamService.getEventTeam(eventId)
    ]);
    
    if (!briefing) {
      throw new Error('Briefing não encontrado. É necessário criar um briefing primeiro.');
    }
    
    if (team.length === 0) {
      throw new Error('Equipe não encontrada. É necessário montar uma equipe primeiro.');
    }
    
    // Algoritmo para gerar timeline com base nas ações do briefing
    // e distribuir tarefas para a equipe disponível
    return timelineService.generateFromBriefing(eventId, briefing, team);
  },
  
  /**
   * Gera entregas automaticamente baseadas no briefing
   */
  generateDeliveriesFromBriefing: async (eventId: string) => {
    // Obtém briefing e equipe
    const [briefing, team] = await Promise.all([
      briefingService.getEventBriefing(eventId),
      teamService.getEventTeam(eventId)
    ]);
    
    if (!briefing) {
      throw new Error('Briefing não encontrado. É necessário criar um briefing primeiro.');
    }
    
    if (team.length === 0) {
      throw new Error('Equipe não encontrada. É necessário montar uma equipe primeiro.');
    }
    
    // Algoritmo para gerar entregas com base no briefing
    // e atribuir para membros da equipe com base em suas funções
    return deliveryService.generateFromBriefing(eventId, briefing, team);
  }
};