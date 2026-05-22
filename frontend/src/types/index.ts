// ── 旅游攻略相关类型 ──

export interface TravelMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  imageUrl?: string;
  loading?: boolean;
}

export interface TravelRequest {
  destination: string;
  days: number;
  preferences: string;
}

export interface TravelResponse {
  taskId: string;
  itinerary: string;
  imageUrl: string;
}

export interface TravelProgressEvent {
  type: 'progress';
  data: {
    message: string;
    step: number;
    total: number;
  };
}

export interface TravelItineraryEvent {
  type: 'itinerary';
  data: {
    content: string;
    destination: string;
    days: number;
  };
}

export interface TravelImageEvent {
  type: 'image';
  data: {
    url: string;
  };
}

export interface TravelCompletedEvent {
  type: 'completed';
  data: {
    message: string;
  };
}

export interface TravelErrorEvent {
  type: 'error';
  data: {
    message: string;
  };
}

export type TravelSSEEvent =
  | TravelProgressEvent
  | TravelItineraryEvent
  | TravelImageEvent
  | TravelCompletedEvent
  | TravelErrorEvent;

// ── 历史记录类型（简化） ──

export interface ChatHistory {
  id: string;
  title: string;
  userMessage: string;
  aiReply: string;
  createdAt: string;
}

// ── 兼容旧类型（供 store / History 页面使用） ──

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  attachments?: any[];
  imageUrl?: string;
  progress?: { step: number; total: number; message: string };
  phase?: 'prompt' | 'complete';
}

export interface ParsedExcel {
  fileId: string;
  fileName: string;
  sheets: any[];
  metadata: { totalRows: number; totalCols: number; sheetCount: number };
}

// ── 用户设置（保留） ──

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large';
  codeFont: 'mono' | 'system';
  messageDensity: 'comfortable' | 'compact';
  defaultPromptModel: string;
  apiKeys: {
    shangtang?: string;
  };
}
