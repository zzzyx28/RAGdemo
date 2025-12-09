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
  role: 'user' | 'assistant';
  content: string;
  isRagSearching?: boolean;
  sources?: Source[];
}

export interface SnackbarState {
  show: boolean;
  text: string;
  color: string;
  timeout: number;
}

