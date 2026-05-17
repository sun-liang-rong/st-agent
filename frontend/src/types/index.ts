// 进度信息
export interface ProgressInfo {
  step: number;
  total: number;
  message: string;
}

// 消息类型
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  attachments?: FileAttachment[];
  imageUrl?: string;
  progress?: ProgressInfo;
}

// 文件附件
export interface FileAttachment {
  id: string;
  name: string;
  type: 'xlsx' | 'xls' | 'csv';
  size: number;
  data?: string;
}

// Sheet信息
export interface SheetInfo {
  name: string;
  rowCount: number;
  colCount: number;
}

// 上传响应
export interface UploadResponse {
  fileId: string;
  fileName: string;
  fileSize: number;
  sheets: SheetInfo[];
  metadata: {
    totalRows: number;
    totalCols: number;
  };
}

// 生成请求
export interface GenerateRequest {
  fileId: string;
  userPrompt: string;
  modelConfig?: ModelConfig;
}

// 模型配置
export interface ModelConfig {
  promptModel: string;
  imageModel: string;
}

// 生成响应
export interface GenerateResponse {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: string;
  message?: string;
}

// 任务状态
export interface TaskStatusResponse {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
  error?: string;
  result?: TaskResult;
}

// 任务结果
export interface TaskResult {
  imageUrl: string;
  prompt: string;
  generatedAt: string;
}

// 对话历史
export interface ChatHistory {
  id: string;
  title: string;
  userPrompt: string;
  generatedPrompt: string;
  imageUrl: string;
  fileName: string;
  createdAt: string;
  updatedAt: string;
}

// 聊天消息历史
export interface ChatMessageHistory {
  id: string;
  title: string;
  userMessage: string;
  aiReply: string;
  createdAt: string;
}

// 用户设置
export interface UserSettings {
  theme: 'light' | 'dark';
  defaultPromptModel: string;
  defaultImageModel: string;
  apiKeys: {
    shangtang?: string;
  };
}

// Sheet数据
export interface Sheet {
  name: string;
  headers: string[];
  rows: Record<string, any>[];
  summary?: {
    numericColumns: string[];
    categoricalColumns: string[];
    dateColumns: string[];
  };
}

// Excel数据
export interface ParsedExcel {
  fileId: string;
  fileName: string;
  sheets: Sheet[];
  metadata: {
    totalRows: number;
    totalCols: number;
    sheetCount: number;
  };
}
