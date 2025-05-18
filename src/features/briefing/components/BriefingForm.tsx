import { useState } from 'react';
import { useEvent } from '@/features/events/context/EventContext';
import { briefingService } from '../services/briefingService';
import { Button, Card, Input, Textarea, Checkbox, TimeInput } from '@/shared/ui';
import { z } from 'zod';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const briefingSchema = z.object({
  showStartTime: z.string(),
  showEndTime: z.string(),
  specialCapture: z.boolean(),
  sponsoredActions: z.array(z.object({
    name: z.string(),
    time: z.string(),
  })).optional(),
  deliveryDeadline: z.date(),
  observations: z.string().optional(),
});

type BriefingFormData = z.infer<typeof briefingSchema>;

export function BriefingForm() {
  const { currentEvent } = useEvent();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sponsoredActions, setSponsoredActions] = useState([
    { id: '1', name: '', time: '' }
  ]);
  
  const { 
    register, 
    control,
    handleSubmit, 
    formState: { errors } 
  } = useForm<BriefingFormData>({
    resolver: zodResolver(briefingSchema),
  });

  const onSubmit = async (data: BriefingFormData) => {
    if (!currentEvent) return;
    
    try {
      setIsSubmitting(true);
      await briefingService.createBriefing(currentEvent.id, {
        ...data,
        sponsoredActions: sponsoredActions.filter(action => action.name && action.time),
      });
      // Redirect ou feedback
    } catch (error) {
      console.error('Failed to save briefing:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addSponsoredAction = () => {
    setSponsoredActions([
      ...sponsoredActions, 
      { id: Date.now().toString(), name: '', time: '' }
    ]);
  };

  const removeSponsoredAction = (id: string) => {
    setSponsoredActions(sponsoredActions.filter(action => action.id !== id));
  };

  const updateSponsoredAction = (id: string, field: 'name' | 'time', value: string) => {
    setSponsoredActions(
      sponsoredActions.map(action => 
        action.id === id ? { ...action, [field]: value } : action
      )
    );
  };

  if (!currentEvent) return <div>Nenhum evento selecionado</div>;
  
  return (
    <Card className="max-w-2xl mx-auto p-6">
      <h2 className="text-xl font-semibold mb-6">
        Briefing do Evento: {currentEvent.name}
      </h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Início do Show</label>
            <Controller
              name="showStartTime"
              control={control}
              render={({ field }) => (
                <TimeInput
                  {...field}
                  error={errors.showStartTime?.message}
                />
              )}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Fim do Show</label>
            <Controller
              name="showEndTime"
              control={control}
              render={({ field }) => (
                <TimeInput
                  {...field}
                  error={errors.showEndTime?.message}
                />
              )}
            />
          </div>
        </div>
        
        <div>
          <Controller
            name="specialCapture"
            control={control}
            render={({ field: { value, onChange, ...field } }) => (
              <div className="flex items-center">
                <Checkbox
                  id="specialCapture"
                  checked={value}
                  onCheckedChange={onChange}
                  {...field}
                />
                <label htmlFor="specialCapture" className="ml-2 text-sm">
                  Captação especial?
                </label>
              </div>
            )}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Ações patrocinadas:</label>
          
          {sponsoredActions.map((action, index) => (
            <div key={action.id} className="flex items-center gap-2 mb-2">
              <Input
                value={action.name}
                onChange={(e) => updateSponsoredAction(action.id, 'name', e.target.value)}
                placeholder="Nome da ação"
                className="flex-grow"
              />
              <TimeInput
                value={action.time}
                onChange={(value) => updateSponsoredAction(action.id, 'time', value || '')}
                placeholder="Horário"
              />
              {index > 0 && (
                <Button
                  type="button"
                  variant="icon"
                  size="sm"
                  onClick={() => removeSponsoredAction(action.id)}
                >
                  ✕
                </Button>
              )}
            </div>
          ))}
          
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="mt-2"
            onClick={addSponsoredAction}
          >
            + Adicionar ação
          </Button>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Prazo de entrega</label>
          <Controller
            name="deliveryDeadline"
            control={control}
            render={({ field }) => (
              <input
                type="date"
                className="w-full rounded border border-gray-300 p-2"
                {...field}
                value={field.value instanceof Date ? field.value.toISOString().substr(0, 10) : ''}
                onChange={(e) => field.onChange(new Date(e.target.value))}
              />
            )}
          />
          {errors.deliveryDeadline?.message && (
            <p className="text-red-500 text-sm mt-1">{errors.deliveryDeadline.message}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Observações</label>
          <Textarea
            {...register('observations')}
            rows={4}
            placeholder="Detalhes adicionais, instruções, ou requisitos especiais..."
            error={errors.observations?.message}
          />
        </div>
        
        <Button 
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Salvando...' : 'Confirmar Briefing'}
        </Button>
      </form>
    </Card>
  );
}