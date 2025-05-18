import { useState, useEffect } from 'react';
import { useEvent } from '@/features/events/context/EventContext';
import { teamService } from '../services/teamService';
import { TeamMember, EventTeamMember } from '../types';
import { Button, Card, List, ListItem, Avatar, Badge, Modal } from '@/shared/ui';
import { CreateTeamMemberForm } from './CreateTeamMemberForm';

export function TeamAssembly() {
  const { currentEvent } = useEvent();
  const [availableMembers, setAvailableMembers] = useState<TeamMember[]>([]);
  const [eventTeam, setEventTeam] = useState<EventTeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateMemberModal, setShowCreateMemberModal] = useState(false);
  
  useEffect(() => {
    async function loadData() {
      if (!currentEvent?.id) return;
      
      try {
        setLoading(true);
        const [members, team] = await Promise.all([
          teamService.getAllMembers(),
          teamService.getEventTeam(currentEvent.id)
        ]);
        
        // Filtra os membros que já fazem parte da equipe
        const filteredMembers = members.filter(
          member => !team.some(teamMember => teamMember.id === member.id)
        );
        
        setAvailableMembers(filteredMembers);
        setEventTeam(team);
      } catch (error) {
        console.error('Failed to load team data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, [currentEvent?.id]);
  
  const addMemberToTeam = async (member: TeamMember) => {
    if (!currentEvent?.id) return;
    
    try {
      const addedMember = await teamService.addMemberToEvent(currentEvent.id, member.id);
      setEventTeam(prev => [...prev, addedMember]);
      setAvailableMembers(prev => prev.filter(m => m.id !== member.id));
    } catch (error) {
      console.error('Failed to add member to team:', error);
    }
  };
  
  const removeMemberFromTeam = async (member: EventTeamMember) => {
    if (!currentEvent?.id) return;
    
    try {
      await teamService.removeMemberFromEvent(currentEvent.id, member.id);
      setEventTeam(prev => prev.filter(m => m.id !== member.id));
      
      // Adiciona de volta à lista de membros disponíveis
      const originalMember = {
        id: member.id,
        name: member.name,
        expertise: member.expertise,
        contactInfo: member.contactInfo
      };
      
      setAvailableMembers(prev => [...prev, originalMember]);
    } catch (error) {
      console.error('Failed to remove member from team:', error);
    }
  };

  const handleCreateMember = async (newMember: Omit<TeamMember, 'id'>) => {
    try {
      const createdMember = await teamService.createMember(newMember);
      setAvailableMembers(prev => [...prev, createdMember]);
      setShowCreateMemberModal(false);
    } catch (error) {
      console.error('Failed to create team member:', error);
    }
  };
  
  if (loading) return <div>Carregando...</div>;
  if (!currentEvent) return <div>Nenhum evento selecionado</div>;
  
  return (
    <div className="space-y-8">
      <h2 className="text-xl font-semibold">Montar Equipe: {currentEvent.name}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Banco de Talentos */}
        <Card className="p-4">
          <h3 className="font-medium mb-4 flex justify-between items-center">
            Banco de Talentos
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowCreateMemberModal(true)}
            >
              Novo Membro +
            </Button>
          </h3>
          
          <List>
            {availableMembers.map(member => (
              <ListItem key={member.id} className="flex justify-between items-center py-3">
                <div className="flex items-center gap-3">
                  <Avatar name={member.name} />
                  <div>
                    <p className="font-medium">{member.name}</p>
                    {member.expertise && (
                      <p className="text-sm text-gray-500">{member.expertise}</p>
                    )}
                  </div>
                </div>
                
                <Button 
                  size="sm"
                  onClick={() => addMemberToTeam(member)}
                >
                  Selecionar
                </Button>
              </ListItem>
            ))}
            
            {availableMembers.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                Todos os membros já foram adicionados à equipe.
              </p>
            )}
          </List>
        </Card>
        
        {/* Equipe do Evento */}
        <Card className="p-4">
          <h3 className="font-medium mb-4">Equipe do Evento</h3>
          
          <List>
            {eventTeam.map(member => (
              <ListItem key={member.id} className="flex justify-between items-center py-3">
                <div className="flex items-center gap-3">
                  <Avatar name={member.name} />
                  <div>
                    <p className="font-medium">{member.name}</p>
                    {member.role && (
                      <Badge variant="outline" className="mt-1">
                        {member.role}
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Button 
                  size="sm"
                  variant="outline"
                  color="danger"
                  onClick={() => removeMemberFromTeam(member)}
                >
                  Remover
                </Button>
              </ListItem>
            ))}
            
            {eventTeam.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                Ainda não há membros na equipe deste evento.
              </p>
            )}
          </List>
        </Card>
      </div>
      
      {/* Modal para criar novo membro */}
      <Modal 
        isOpen={showCreateMemberModal} 
        onClose={() => setShowCreateMemberModal(false)}
        title="Adicionar Novo Membro"
      >
        <CreateTeamMemberForm onSubmit={handleCreateMember} />
      </Modal>
    </div>
  );
}