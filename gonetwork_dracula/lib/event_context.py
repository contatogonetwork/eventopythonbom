class EventContext:
    """
    Implementação de Singleton para compartilhar informações do evento atual
    entre diferentes janelas da aplicação.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventContext, cls).__new__(cls)
            cls._instance._event_id = None
            cls._instance._event_name = None
            cls._instance._observers = []
        return cls._instance
    
    @property
    def event_id(self):
        return self._event_id
    
    @event_id.setter
    def event_id(self, value):
        self._event_id = value
        self._notify_observers()
    
    @property
    def event_name(self):
        return self._event_name
    
    @event_name.setter
    def event_name(self, value):
        self._event_name = value
        self._notify_observers()
    
    def add_observer(self, observer):
        """
        Adiciona um observador que será notificado quando o evento mudar
        
        O observador deve ser um objeto com um método 'on_event_changed(event_id, event_name)'
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove um observador da lista de notificações"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self):
        """Notifica todos os observadores sobre a mudança do evento"""
        # Criar uma cópia da lista para permitir que observadores se removam durante a notificação
        observers_to_notify = self._observers.copy()
        for observer in observers_to_notify:
            try:
                if observer in self._observers:  # Verificar se ainda está na lista
                    observer.on_event_changed(self._event_id, self._event_name)
            except Exception as e:
                print(f"Erro ao notificar observador: {e}")
                # Remove automaticamente observadores que geram erros
                if observer in self._observers:
                    self._observers.remove(observer)
    
    def clear(self):
        """Limpa o contexto do evento atual"""
        self._event_id = None
        self._event_name = None
        self._notify_observers()


# Uso do EventContext nas janelas
class EventAwareWindow:
    """
    Classe abstrata que implementa a funcionalidade para
    janelas que precisam estar cientes do evento atual
    """
    def __init__(self):
        self.event_context = EventContext()
        self._is_observer_registered = False
        self.register_as_observer()
        
    def register_as_observer(self):
        """Registra a janela como observadora"""
        if not self._is_observer_registered:
            self.event_context.add_observer(self)
            self._is_observer_registered = True
    
    def unregister_as_observer(self):
        """Remove a janela como observadora"""
        if self._is_observer_registered:
            self.event_context.remove_observer(self)
            self._is_observer_registered = False
        
    def on_event_changed(self, event_id, event_name):
        """
        Método chamado quando o evento atual é alterado
        Implementar nas classes filhas
        """
        pass
    
    def closeEvent(self, event):
        """Método chamado quando a janela é fechada via Qt"""
        self.unregister_as_observer()
        super().closeEvent(event) if hasattr(super(), 'closeEvent') else event.accept()
    
    def __del__(self):
        """Garante que o observador é removido ao destruir a janela"""
        try:
            self.unregister_as_observer()
        except:
            # Em caso de erro durante a destruição, não propagar exceções
            pass