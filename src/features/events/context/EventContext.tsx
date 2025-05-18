import React, { createContext, useContext, useState, useEffect } from 'react';
import { Event, EventContextType } from '../types';
import { eventService } from '../services/eventService';

const EventContext = createContext<EventContextType | undefined>(undefined);

export function EventProvider({ children }: { children: React.ReactNode }) {
  const [events, setEvents] = useState<Event[]>([]);
  const [currentEvent, setCurrentEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const data = await eventService.getAllEvents();
        setEvents(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch events');
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const createEvent = async (eventData: Omit<Event, 'id'>) => {
    try {
      const newEvent = await eventService.createEvent(eventData);
      setEvents(prevEvents => [...prevEvents, newEvent]);
      setCurrentEvent(newEvent);
      return newEvent;
    } catch (err) {
      setError('Failed to create event');
      throw err;
    }
  };

  const selectEvent = (eventId: string) => {
    const event = events.find(e => e.id === eventId) || null;
    setCurrentEvent(event);
    return event;
  };

  const updateEvent = async (id: string, data: Partial<Event>) => {
    try {
      const updatedEvent = await eventService.updateEvent(id, data);
      setEvents(prevEvents => 
        prevEvents.map(event => event.id === id ? updatedEvent : event)
      );
      if (currentEvent?.id === id) {
        setCurrentEvent(updatedEvent);
      }
      return updatedEvent;
    } catch (err) {
      setError('Failed to update event');
      throw err;
    }
  };

  return (
    <EventContext.Provider value={{
      events,
      currentEvent,
      loading,
      error,
      createEvent,
      selectEvent,
      updateEvent,
    }}>
      {children}
    </EventContext.Provider>
  );
}

export const useEvent = () => {
  const context = useContext(EventContext);
  if (!context) {
    throw new Error('useEvent must be used within an EventProvider');
  }
  return context;
};