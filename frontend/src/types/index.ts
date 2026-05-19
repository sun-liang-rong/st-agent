// 进度信息
export interface ProgressInfo {
  step: number;
  total: number;
  message: string;
}

// ── 看板相关类型 ──

export interface DashboardChart {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'radar' | 'funnel' | 'kline' | 'heatmap' | 'treemap';
  size: 'full' | 'half' | 'third';
  option: Record<string, any>;
}

export interface DashboardSpec {
  title: string;
  description?: string;
  charts: DashboardChart[];
}

// 消息类型
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  attachments?: FileAttachment[];
  imageUrl?: string;
  dashboardSpec?: DashboardSpec;
  progress?: ProgressInfo;
  /** 待用户确认的 AI 生成提示词（两阶段模式） */
  promptForReview?: string;
  /** 消息所处的阶段: 'prompt' = 等待用户确认提示词, 'complete' = 已完成 */
  phase?: 'prompt' | 'complete';
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
  selectedColumns?: string[];
  chartType?: string;
  chartTitle?: string;
}

// 模型配置
export interface ModelConfig {
  promptModel: string;
  imageModel: string;
}

// 生成响应
export interface GenerateResponse {
  taskId: string;
  status: 'pending' | 'processing' | 'spec_ready' | 'completed' | 'failed';
  dashboardSpec?: DashboardSpec;
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
  dashboardSpec?: DashboardSpec;
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
  fontSize: 'small' | 'medium' | 'large';
  codeFont: 'mono' | 'system';
  messageDensity: 'comfortable' | 'compact';
  defaultPromptModel: string;
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

// ── 数据预览相关类型 ──

// 列信息
export interface ColumnInfo {
  name: string;
  dtype: 'numeric' | 'text' | 'datetime';
  nullCount: number;
  stats?: {
    min: number | null;
    max: number | null;
    mean: number | null;
    median: number | null;
  };
  uniqueValues?: number;
}

// 预览响应
export interface PreviewResponse {
  columns: ColumnInfo[];
  rows: any[][];
  totalRows: number;
  totalCols: number;
  columnNames: string[];
}

// AI 建议提示词响应
export interface SuggestResponse {
  suggestion: string;
}

// 图表类型
export type ChartType = 'bar' | 'line' | 'pie' | 'scatter' | 'combo';

// 图表类型中文映射
export const CHART_TYPE_LABELS: Record<ChartType, string> = {
  bar: '柱状图',
  line: '折线图',
  pie: '饼图',
  scatter: '散点图',
  combo: '组合看板',
};
