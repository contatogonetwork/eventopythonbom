// Tipos básicos compartilhados entre os módulos

export interface Event {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  location: string;
  responsiblePerson: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TeamMember {
  id: string;
  name: string;
  expertise?: string;
  contactInfo?: string;
  avatar?: string;
}

export interface EventTeamMember extends TeamMember {
  role?: string;
  assignedTasks?: number;
}

export interface Briefing {
  id: string;
  eventId: string;
  showStartTime: string;
  showEndTime: string;
  specialCapture: boolean;
  sponsoredActions?: SponsoredAction[];
  deliveryDeadline: Date;
  observations?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SponsoredAction {
  name: string;
  time: string;
}

export interface TimelineItem {
  id: string;
  eventId: string;
  title: string;
  startTime: string;
  endTime?: string;
  assignedTo?: EventTeamMember;
  status: 'pending' | 'in-progress' | 'completed';
  notes?: string;
}

export interface Delivery {
  id: string;
  eventId: string;
  title: string;
  description?: string;
  dueDate: Date;
  assignedTo?: EventTeamMember;
  status: 'pending' | 'in-review' | 'approved' | 'rejected';
  versions?: DeliveryVersion[];
  approvers?: Approver[];
  reminderSent?: boolean;
}

export interface DeliveryVersion {
  id: string;
  deliveryId: string;
  fileUrl: string;
  fileName: string;
  fileSize: number;
  uploadedAt: Date;
  uploadedBy: string;
  notes?: string;
}

export interface Approver {
  id: string;
  name: string;
  email: string;
  status: 'pending' | 'approved' | 'rejected';
  commentDate?: Date;
  comments?: string;
}