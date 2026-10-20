// =====================================================
// SessionPlanner.ets - 学习会话任务编排器
// 将线性刷词升级为多任务混编的智能学习系统
// =====================================================

import { WordItem, WordStatus, Rating } from '../model/WordModel';

/**
 * 任务类型枚举
 */
export enum TaskType {
  STORY = 'STORY'           // 情境故事（点击词释义）
}

/**
 * 错因类型枚举
 */
export enum ErrorType {
  MEANING = 'MEANING',       // 释义错误
  USAGE = 'USAGE',           // 用法错误
  SPELLING = 'SPELLING',       // 拼写错误
  PRONUNCIATION = 'PRONUNCIATION', // 发音错误
  CONFUSION = 'CONFUSION'     // 混淆错误（形近词/音近词）
}

/**
 * 任务难度级别
 */
export enum TaskDifficulty {
  EASY = 1,
  MEDIUM = 2,
  HARD = 3
}

/**
 * 学习任务项
 */
export class TaskItem {
  id: string;
  type: TaskType;
  word: WordItem;
  difficulty: TaskDifficulty;
  content: string;              // 任务内容（故事/句子/问题等）
  options?: string[];            // 选择题选项
  correctAnswer?: string;        // 正确答案
  userAnswer?: string;          // 用户答案
  isCorrect?: boolean;          // 是否正确
  errorTag?: ErrorType;         // 错因标签
  reflection?: string;           // 用户反思（错因复盘）
  isReinforcement: boolean;     // 是否为强化任务（遗忘后插入）
  priority: number;             // 优先级（0=最高）
  estimatedTime: number;        // 预估时间（秒）
  preferredOffset?: number;

  constructor(
    id: string,
    type: TaskType,
    word: WordItem,
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM,
    content: string = '',
    isReinforcement: boolean = false,
    priority: number = 0,
    estimatedTime: number = 20
  ) {
    this.id = id;
    this.type = type;
    this.word = word;
    this.difficulty = difficulty;
    this.content = content;
    this.isReinforcement = isReinforcement;
    this.priority = priority;
    this.estimatedTime = estimatedTime;
  }

  /**
   * 获取任务类型的中文名称
   */
  getTypeName(): string {
    return '情境故事';
  }

  /**
   * 获取任务类型图标
   */
  getTypeIcon(): string {
    return '📖';
  }

  /**
   * 检查任务是否完成
   */
  isCompleted(): boolean {
    return this.userAnswer !== undefined;
  }

  /**
   * 获取任务状态文本
   */
  getStatusText(): string {
    if (!this.isCompleted()) {
      return '待完成';
    }
    if (this.isCorrect === undefined) {
      return '待评价';
    }
    return this.isCorrect ? '正确' : '错误';
  }
}

/**
 * 会话编排配置
 */
export class SessionConfig {
  storyRatio: number;           // 故事任务比例（0-1）
  clozeRatio: number;           // 填空任务比例
  choiceRatio: number;           // 选择题比例
  collocationRatio: number;      // 搭配任务比例
  pronunciationRatio: number;   // 发音任务比例
  maxTasksPerWord: number;      // 每个词最多任务数
  reinforcementCount: number;   // 遗忘后插入强化任务数

  constructor(
    storyRatio: number = 0.4,
    clozeRatio: number = 0.25,
    choiceRatio: number = 0.15,
    collocationRatio: number = 0.15,
    pronunciationRatio: number = 0.05,
    maxTasksPerWord: number = 3,
    reinforcementCount: number = 2
  ) {
    this.storyRatio = storyRatio;
    this.clozeRatio = clozeRatio;
    this.choiceRatio = choiceRatio;
    this.collocationRatio = collocationRatio;
    this.pronunciationRatio = pronunciationRatio;
    this.maxTasksPerWord = maxTasksPerWord;
    this.reinforcementCount = reinforcementCount;
  }

  /**
   * 验证配置是否有效
   */
  isValid(): boolean {
    const total = this.storyRatio + this.clozeRatio + this.choiceRatio +
                  this.collocationRatio + this.pronunciationRatio;
    return Math.abs(total - 1.0) < 0.01;
  }
}

/**
 * 学习会话编排器
 */
export class SessionPlanner {
  private static instance: SessionPlanner | null = null;
  private config: SessionConfig;
  private taskIdCounter: number = 0;

  private constructor() {
    this.config = new SessionConfig();
  }

  /**
   * 获取单例实例
   */
  static getInstance(): SessionPlanner {
    if (SessionPlanner.instance === null) {
      SessionPlanner.instance = new SessionPlanner();
    }
    return SessionPlanner.instance;
  }

  /**
   * 设置编排配置
   */
  setConfig(config: SessionConfig): void {
    if (config.isValid()) {
      this.config = config;
    } else {
      console.warn('[SessionPlanner] Invalid config, using default');
    }
  }

  /**
   * 获取当前配置
   */
  getConfig(): SessionConfig {
    return this.config;
  }

  /**
   * 生成任务ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${this.taskIdCounter++}`;
  }

  /**
   * 生成基础任务（V1: 仅情境故事）
   */
  private generateBaseTasks(word: WordItem): TaskItem[] {
    const tasks: TaskItem[] = [];
    const isNewWord = word.status === WordStatus.NEW;

    // V1: 仅生成故事任务
    tasks.push(new TaskItem(
      this.generateTaskId(),
      TaskType.STORY,
      word,
      isNewWord ? TaskDifficulty.EASY : TaskDifficulty.MEDIUM,
      '',
      false,
      isNewWord ? 1 : 0,
      30
    ));

    return tasks;
  }

  /**
   * 生成强化任务（遗忘后插入）
   */
  generateReinforcementTasks(word: WordItem, rating: Rating, allowOnPass: boolean = false): TaskItem[] {
    const tasks: TaskItem[] = [];

    // 只有 AGAIN 或 HARD 才生成强化任务
    if (!allowOnPass && (rating === Rating.GOOD || rating === Rating.EASY)) {
      return tasks;
    }

    // V1: 仅保留语境阅读强化任务
    tasks.push(new TaskItem(
      this.generateTaskId(),
      TaskType.STORY,
      word,
      TaskDifficulty.EASY,
      '',
      true,
      0,
      30
    ));

    // 限制强化任务数量
    return tasks.slice(0, this.config.reinforcementCount);
  }



  /**
   * 为单词列表编排完整会话
   */
  planSession(words: WordItem[]): TaskItem[] {
    const allTasks: TaskItem[] = [];

    for (const word of words) {
      const wordTasks = this.generateBaseTasks(word);
      allTasks.push(...wordTasks);
    }

    // 按优先级排序（强化任务优先）
    allTasks.sort((a: TaskItem, b: TaskItem): number => {
      if (a.isReinforcement && !b.isReinforcement) return -1;
      if (!a.isReinforcement && b.isReinforcement) return 1;
      return a.priority - b.priority;
    });

    return allTasks;
  }

  /**
   * V1 微语境学习会话（仅 STORY）
   */
  planMicroContextSession(words: WordItem[]): TaskItem[] {
    const tasks: TaskItem[] = [];
    for (const word of words) {
      tasks.push(new TaskItem(
        this.generateTaskId(),
        TaskType.STORY,
        word,
        this.getRecommendedDifficulty(word),
        '',
        false,
        0,
        30
      ));
    }
    return tasks;
  }

  /**
   * 计算会话总预估时间（分钟）
   */
  estimateSessionTime(tasks: TaskItem[]): number {
    const totalSeconds = tasks.reduce((sum: number, task: TaskItem): number => {
      return sum + task.estimatedTime;
    }, 0);
    return Math.round(totalSeconds / 60);
  }

  /**
   * 获取任务类型分布统计
   */
  getTaskDistribution(tasks: TaskItem[]): Map<TaskType, number> {
    const distribution = new Map<TaskType, number>();

    for (const task of tasks) {
      const count = distribution.get(task.type) ?? 0;
      distribution.set(task.type, count + 1);
    }

    return distribution;
  }

  /**
   * 检查是否需要为单词生成强化任务
   */
  shouldReinforce(word: WordItem, rating: Rating): boolean {
    return rating === Rating.AGAIN || rating === Rating.HARD;
  }

  /**
   * 获取推荐的任务难度
   */
  getRecommendedDifficulty(word: WordItem): TaskDifficulty {
    // 根据单词状态推荐难度
    if (word.status === WordStatus.NEW) {
      return TaskDifficulty.EASY;
    } else if (word.status === WordStatus.LEARNING) {
      return TaskDifficulty.MEDIUM;
    } else {
      return TaskDifficulty.HARD;
    }
  }

  /**
   * 生成会话摘要
   */
  generateSessionSummary(tasks: TaskItem[]): string {
    const totalTasks = tasks.length;
    const reinforcementTasks = tasks.filter((t: TaskItem): boolean => t.isReinforcement).length;
    const estimatedTime = this.estimateSessionTime(tasks);
    const distribution = this.getTaskDistribution(tasks);

    let summary = `会话包含 ${totalTasks} 个任务，预计耗时 ${estimatedTime} 分钟\n`;
    summary += `强化任务: ${reinforcementTasks} 个\n`;
    summary += '任务分布:\n';

    distribution.forEach((count: number, type: string) => {
      const taskItem = new TaskItem('', type as TaskType, new WordItem());
      summary += `  ${taskItem.getTypeName()}: ${count} 个\n`;
    });

    return summary;
  }
}
