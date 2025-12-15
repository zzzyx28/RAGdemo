export interface KnowledgeFile {
  name: string;
  type: string;
  size: string;
}

export interface Source {
  filename: string;
  page: number;
}

export interface Message {
  id?: number;
  conversation_id?: number;
  role: 'user' | 'assistant';
  content: string;
  isRagSearching?: boolean;
  sources?: Source[];
  created_at?: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: Message[];
}

export interface SnackbarState {
  show: boolean;
  text: string;
  color: string;
  timeout: number;
}

