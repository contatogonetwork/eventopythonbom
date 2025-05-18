import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useEvent } from '../context/EventContext';
import { Button, Input, DatePicker, Card } from '@/shared/ui';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const eventSchema = z.object({
  name: z.string().min(3, 'Nome do evento precisa ter pelo menos 3 caracteres'),
  startDate: z.date(),
  endDate: z.date(),
  location: z.string().min(3, 'Localização é obrigatória'),
  responsiblePerson: z.string().min(3, 'Responsável é obrigatório'),
});

type EventFormData = z.infer<typeof eventSchema>;

export function CreateEventForm() {
  const router = useRouter();
  const { createEvent } = useEvent();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    control
  } = useForm<EventFormData>({
    resolver: zodResolver(eventSchema),
  });

  const onSubmit = async (data: EventFormData) => {
    try {
      setIsSubmitting(true);
      const newEvent = await createEvent(data);
      router.push(`/events/${newEvent.id}`);
    } catch (error) {
      console.error('Failed to create event:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Criar Novo Evento</h1>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-1">Nome do Evento</label>
          <Input
            {...register('name')}
            placeholder="Ex: DELUX"
            error={errors.name?.message}
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Data Início</label>
            <DatePicker 
              name="startDate"
              control={control}
              error={errors.startDate?.message}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Data Fim</label>
            <DatePicker 
              name="endDate"
              control={control}
              error={errors.endDate?.message}
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Local</label>
          <Input
            {...register('location')}
            placeholder="Ex: PARADOR"
            error={errors.location?.message}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Responsável</label>
          <Input
            {...register('responsiblePerson')}
            placeholder="Ex: Danilo"
            error={errors.responsiblePerson?.message}
          />
        </div>
        
        <Button 
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Criando...' : 'Criar Evento'}
        </Button>
      </form>
    </Card>
  );
}