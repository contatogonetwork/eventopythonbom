import { useEffect, useState } from 'react';
import { useEvent } from '../context/EventContext';
import { briefingService } from '@/features/briefing/services/briefingService'; 
import { teamService } from '@/features/team/services/teamService';
import { timelineService } from '@/features/timeline/services/timelineService';
import { deliveryService } from '@/features/deliveries/services/deliveryService';
import { 
  Card, 
  Button, 
  Badge,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/shared/ui';
import { TeamAssembly } from '@/features/team/components/TeamAssembly';
import { BriefingForm } from '@/features/briefing/components/BriefingForm';
import { Timeline } from '@/features/timeline/components/Timeline';
import { DeliveryList } from '@/features/deliveries/components/DeliveryList';
import { formatDate } from '@/shared/utils/dateUtils';
import { Briefing, EventTeamMember } from '@/features/types';

export function EventDashboard({ eventId }: { eventId: string }) {
  const { selectEvent, currentEvent } = useEvent();
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [team, setTeam] = useState<EventTeamMember[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [hasTimeline, setHasTimeline] = useState(false);
  const [hasDeliveries, setHasDeliveries] = useState(false);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadEventData() {
      try {
        setLoading(true);
        
        // Carrega o evento atual
        const event = await selectEvent(eventId);
        if (!event) throw new Error('Evento não encontrado');
        
        // Carrega dados relacionados ao evento
        const [briefingData, teamData, hasTimelineData, hasDeliveriesData] = await Promise.all([
          briefingService.getEventBriefing(eventId).catch(() => null),
          teamService.getEventTeam(eventId),
          timelineService.checkEventHasTimeline(eventId),
          deliveryService.checkEventHasDeliveries(eventId)
        ]);
        
        setBriefing(briefingData);
        setTeam(teamData);
        setHasTimeline(hasTimelineData);
        setHasDeliveries(hasDeliveriesData);
      } catch (error) {
        console.error('Failed to load event data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadEventData();
  }, [eventId, selectEvent]);
  
  const generateTimelineFromBriefing = async () => {
    if (!currentEvent?.id || !briefing) return;
    
    try {
      await timelineService.generateFromBriefing(currentEvent.id, briefing);
      setHasTimeline(true);
      setActiveTab('timeline');
    } catch (error) {
      console.error('Failed to generate timeline:', error);
    }
  };
  
  const generateDeliveriesFromBriefing = async () => {
    if (!currentEvent?.id || !briefing) return;
    
    try {
      await deliveryService.generateFromBriefing(currentEvent.id, briefing);
      setHasDeliveries(true);
      setActiveTab('deliveries');
    } catch (error) {
      console.error('Failed to generate deliveries:', error);
    }
  };
  
  if (loading) return <div>Carregando...</div>;
  if (!currentEvent) return <div>Evento não encontrado</div>;
  
  return (
    <div className="space-y-6">
      {/* Cabeçalho do evento */}
      <Card className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold">{currentEvent.name}</h1>
            <div className="flex items-center gap-2 mt-2">
              <Badge>{formatDate(currentEvent.startDate)} a {formatDate(currentEvent.endDate)}</Badge>
              <Badge variant="outline">{currentEvent.location}</Badge>
            </div>
            <p className="text-gray-500 mt-1">Responsável: {currentEvent.responsiblePerson}</p>
          </div>
        </div>
      </Card>
      
      {/* Ações principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Button 
          onClick={() => setActiveTab('team')}
          className="h-24"
          variant={team.length > 0 ? "default" : "outline"}
        >
          {team.length > 0 ? `Equipe (${team.length})` : 'Montar Equipe'}
        </Button>
        
        <Button 
          onClick={() => setActiveTab('briefing')}
          className="h-24"
          variant={briefing ? "default" : "outline"}
        >
          {briefing ? 'Editar Briefing' : 'Gerar Briefing'}
        </Button>
        
        <Button 
          onClick={() => hasTimeline ? setActiveTab('timeline') : generateTimelineFromBriefing()}
          className="h-24"
          variant={hasTimeline ? "default" : "outline"}
          disabled={!briefing}
        >
          {hasTimeline ? 'Ver Cronograma' : 'Iniciar Cronograma'}
        </Button>
        
        <Button 
          onClick={() => hasDeliveries ? setActiveTab('deliveries') : generateDeliveriesFromBriefing()}
          className="h-24"
          variant={hasDeliveries ? "default" : "outline"}
          disabled={!briefing}
        >
          {hasDeliveries ? 'Ver Entregas' : 'Cadastrar Entregas'}
        </Button>
      </div>
      
      {/* Conteúdo baseado na aba */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="team">Equipe</TabsTrigger>
          <TabsTrigger value="briefing">Briefing</TabsTrigger>
          <TabsTrigger value="timeline" disabled={!hasTimeline}>Cronograma</TabsTrigger>
          <TabsTrigger value="deliveries" disabled={!hasDeliveries}>Entregas</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Resumo de cada seção */}
            {/* Status atual do evento */}
            {/* Próximas ações */}
          </div>
        </TabsContent>
        
        <TabsContent value="team" className="mt-6">
          <TeamAssembly />
        </TabsContent>
        
        <TabsContent value="briefing" className="mt-6">
          <BriefingForm />
        </TabsContent>
        
        <TabsContent value="timeline" className="mt-6">
          {hasTimeline ? <Timeline eventId={eventId} /> : (
            <Card className="p-6 text-center">
              <p className="mb-4">Nenhum cronograma foi gerado ainda.</p>
              <Button onClick={generateTimelineFromBriefing} disabled={!briefing}>
                Gerar Cronograma do Briefing
              </Button>
            </Card>
          )}
        </TabsContent>
        
        <TabsContent value="deliveries" className="mt-6">
          {hasDeliveries ? <DeliveryList eventId={eventId} /> : (
            <Card className="p-6 text-center">
              <p className="mb-4">Nenhuma entrega foi cadastrada ainda.</p>
              <Button onClick={generateDeliveriesFromBriefing} disabled={!briefing}>
                Gerar Entregas do Briefing
              </Button>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}