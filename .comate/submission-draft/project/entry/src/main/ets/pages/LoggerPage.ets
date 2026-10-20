import router from '@ohos.router';
import promptAction from '@ohos.promptAction';
import type common from '@ohos.app.ability.common';
import { DesignTokens } from '../model/DesignTokens';
import { ColorsInterface } from '../model/TokenInterfaces';
import { ThemeManager } from '../manager/ThemeManager';
import { logger, LogStats, LogEntry, LogLevel } from '../utils/Logger';
import { DataFileTransfer } from '../sync/DataFileTransfer';
import { hilog } from '@kit.PerformanceAnalysisKit';

interface LevelFilterOption {
  level: LogLevel | null;
  label: string;
}

@Entry
@Component
struct LoggerPage {
  @State logStats: LogStats = { total: 0, debug: 0, info: 0, warn: 0, error: 0 };
  @State isLogExporting: boolean = false;
  @State isDiagnosticExporting: boolean = false;
  @State searchKeyword: string = '';
  @State selectedLevelIndex: number = 0;
  @State displayedLogs: LogEntry[] = [];
  @State enableHilog: boolean = true;
  @State enablePersistence: boolean = false;
  @State persistenceIncludeInfo: boolean = false;
  @State persistenceMaxMB: number = 2;
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();

  private readonly PREVIEW_COUNT = 100;
  private readonly PERSISTENCE_MB_OPTIONS: number[] = [1, 2, 3, 4, 5];
  private readonly LEVEL_FILTERS: LevelFilterOption[] = [
    { level: null, label: '全部' },
    { level: LogLevel.ERROR, label: '错误' },
    { level: LogLevel.WARN, label: '警告' },
    { level: LogLevel.INFO, label: '信息' },
    { level: LogLevel.DEBUG, label: '调试' }
  ];

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  private refreshDisplayedLogs(): void {
    const filter = this.LEVEL_FILTERS[this.selectedLevelIndex];
    if (this.searchKeyword.length > 0) {
      this.displayedLogs = logger.searchLogs(this.searchKeyword, filter.level ?? undefined)
        .slice(-this.PREVIEW_COUNT);
    } else if (filter.level !== null) {
      this.displayedLogs = logger.getLogsByLevel(filter.level).slice(-this.PREVIEW_COUNT);
    } else {
      this.displayedLogs = logger.getRecentLogs(this.PREVIEW_COUNT);
    }
    this.logStats = logger.getStats();
    this.enableHilog = logger.isHilogEnabled();
    this.enablePersistence = logger.isPersistenceEnabled();
    this.persistenceIncludeInfo = logger.getPersistenceIncludeInfo();
    this.persistenceMaxMB = logger.getPersistenceMaxBytesInMB();
  }

  private updateHilogEnabled(value: boolean): void {
    this.enableHilog = value;
    const context = getContext(this) as common.UIAbilityContext;
    logger.setEnableHilog(value, context);
  }

  private updatePersistenceEnabled(value: boolean): void {
    this.enablePersistence = value;
    const context = getContext(this) as common.UIAbilityContext;
    logger.setEnablePersistence(value, context);
  }

  private updatePersistenceIncludeInfo(value: boolean): void {
    this.persistenceIncludeInfo = value;
    const context = getContext(this) as common.UIAbilityContext;
    logger.setPersistenceIncludeInfo(value, context);
  }

  private updatePersistenceCapacity(index: number): void {
    const clamped = Math.max(0, Math.min(index, this.PERSISTENCE_MB_OPTIONS.length - 1));
    this.persistenceMaxMB = this.PERSISTENCE_MB_OPTIONS[clamped];
    const context = getContext(this) as common.UIAbilityContext;
    logger.setPersistenceMaxBytesInMB(this.persistenceMaxMB, context);
  }

  private formatTimestamp(ts: number): string {
    const d = new Date(ts);
    const pad = (n: number): string => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  private getLevelBadge(level: LogLevel): string {
    switch (level) {
      case LogLevel.DEBUG: return 'D';
      case LogLevel.INFO: return 'I';
      case LogLevel.WARN: return 'W';
      case LogLevel.ERROR: return 'E';
      default: return '?';
    }
  }

  private getLevelColor(level: LogLevel): ResourceColor {
    switch (level) {
      case LogLevel.DEBUG: return this.colors.GRAY_500;
      case LogLevel.INFO: return this.colors.PRIMARY;
      case LogLevel.WARN: return '#F59E0B';
      case LogLevel.ERROR: return this.colors.ERROR;
      default: return this.colors.GRAY_500;
    }
  }

  private makeLogFileName(): string {
    const d = new Date();
    const pad = (n: number): string => String(n).padStart(2, '0');
    const y = d.getFullYear();
    const m = pad(d.getMonth() + 1);
    const day = pad(d.getDate());
    const hh = pad(d.getHours());
    const mm = pad(d.getMinutes());
    return `vignette_logs_${y}${m}${day}_${hh}${mm}.txt`;
  }

  private makeDiagnosticFileName(): string {
    const d = new Date();
    const pad = (n: number): string => String(n).padStart(2, '0');
    const y = d.getFullYear();
    const m = pad(d.getMonth() + 1);
    const day = pad(d.getDate());
    const hh = pad(d.getHours());
    const mm = pad(d.getMinutes());
    return `vignette_diagnostic_${y}${m}${day}_${hh}${mm}.txt`;
  }

  private async exportLogs(): Promise<void> {
    if (this.isLogExporting) return;
    this.isLogExporting = true;
    logger.info('Logger', '开始导出日志');
    try {
      const context = getContext(this) as common.UIAbilityContext;
      const logText = logger.exportToText();
      const saveRes = await DataFileTransfer.saveJsonToPickedFile(context, this.makeLogFileName(), logText);
      if (saveRes.ok) {
        promptAction.showToast({ message: '日志已导出', duration: 1500 });
        logger.info('Logger', '日志导出成功');
      } else if (saveRes.cancelled) {
        promptAction.showToast({ message: '已取消导出', duration: 1500 });
        logger.info('Logger', '日志导出取消');
      } else {
        promptAction.showToast({ message: `导出失败: ${saveRes.error}`, duration: 2000 });
        logger.error('Logger', '日志导出失败', saveRes.error);
      }
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : String(e);
      promptAction.showToast({ message: `导出失败: ${errMsg}`, duration: 2000 });
      logger.error('Logger', '日志导出异常', errMsg);
    } finally {
      this.isLogExporting = false;
    }
  }

  private async exportDiagnostic(): Promise<void> {
    if (this.isDiagnosticExporting) return;
    this.isDiagnosticExporting = true;
    logger.info('Logger', '开始生成诊断报告');
    try {
      const context = getContext(this) as common.UIAbilityContext;
      const report = logger.generateDiagnosticReport();
      const saveRes = await DataFileTransfer.saveJsonToPickedFile(context, this.makeDiagnosticFileName(), report);
      if (saveRes.ok) {
        promptAction.showToast({ message: '诊断报告已导出', duration: 1500 });
        logger.info('Logger', '诊断报告导出成功');
      } else if (saveRes.cancelled) {
        promptAction.showToast({ message: '已取消导出', duration: 1500 });
      } else {
        promptAction.showToast({ message: `导出失败: ${saveRes.error}`, duration: 2000 });
        logger.error('Logger', '诊断报告导出失败', saveRes.error);
      }
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : String(e);
      promptAction.showToast({ message: `导出失败: ${errMsg}`, duration: 2000 });
      logger.error('Logger', '诊断报告导出异常', errMsg);
    } finally {
      this.isDiagnosticExporting = false;
    }
  }

  private clearLogs(): void {
    logger.clearLogs();
    this.refreshDisplayedLogs();
    promptAction.showToast({ message: '日志已清空', duration: 1500 });
  }

  aboutToAppear(): void {
    this.refreshDisplayedLogs();
    logger.info('Logger', '进入日志页面');
  }

  @Builder
  private buildHeader() {
    Row() {
      Text('←')
        .fontSize(DesignTokens.Typography.FONT_SIZE_2XL)
        .fontColor(this.colors.GRAY_900)
        .onClick(() => { router.back(); })

      Text('日志与调试')
        .fontSize(DesignTokens.Typography.FONT_SIZE_XL)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_BOLD)
        .fontColor(this.colors.GRAY_900)
        .margin({ left: DesignTokens.Spacing.LG })

      Blank()
    }
    .width('100%')
    .height(56)
    .padding({ left: DesignTokens.Layout.CONTAINER_PADDING, right: DesignTokens.Layout.CONTAINER_PADDING })
    .backgroundColor(this.colors.SURFACE_ELEVATED)
    .shadow({ color: this.colors.SHADOW_LIGHT, radius: 4, offsetX: 0, offsetY: 2 })
  }

  @Builder
  private buildStatsBar() {
    Row() {
      Text(`共 ${this.logStats.total} 条`)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_SECONDARY)

      Blank()

      if (this.logStats.error > 0) {
        Text(`错误 ${this.logStats.error}`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.ERROR)
          .margin({ right: DesignTokens.Spacing.SM })
      }
      if (this.logStats.warn > 0) {
        Text(`警告 ${this.logStats.warn}`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor('#F59E0B')
      }
    }
    .width('100%')
    .padding({ bottom: DesignTokens.Spacing.SM })
  }

  @Builder
  private buildOutputCard() {
    Column() {
      Text('日志输出')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_BOLD)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')

      Text('配置日志输出渠道，HiLog 可在 DevEco Studio 中实时查看。')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_SECONDARY)
        .width('100%')
        .margin({ top: 6, bottom: DesignTokens.Spacing.MD })

      Row() {
        Column() {
          Text('HiLog 输出')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.TEXT_PRIMARY)
          Text('输出到系统日志，在 IDE 中查看')
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.colors.TEXT_TERTIARY)
            .margin({ top: 4 })
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        Toggle({ type: ToggleType.Switch, isOn: this.enableHilog })
          .selectedColor(this.colors.PRIMARY)
          .switchPointColor(this.colors.WHITE)
          .onChange((value: boolean) => {
            this.updateHilogEnabled(value);
          })
      }
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

      Row() {
        Column() {
          Text('测试 HiLog')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.TEXT_PRIMARY)
          Text('发送一条测试日志到 HiLog')
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.colors.TEXT_TERTIARY)
            .margin({ top: 4 })
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        Button('发送')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .height(32)
          .onClick(() => {
            hilog.info(0x6539, 'Vignette', 'HiLog 测试日志 - 时间: %{public}s', new Date().toLocaleTimeString());
            promptAction.showToast({ message: '测试日志已发送', duration: 1500 });
          })
      }
      .width('100%')
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
    .margin({ bottom: DesignTokens.Spacing.MD })
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
  }

  @Builder
  private buildPersistenceCard() {
    Column() {
      Text('持久化策略')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_BOLD)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')

      Text('默认仅落盘 WARN/ERROR，启动时自动回放最近日志用于崩溃前上下文。')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_SECONDARY)
        .width('100%')
        .margin({ top: 6, bottom: DesignTokens.Spacing.MD })

      Row() {
        Column() {
          Text('启用日志持久化')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.TEXT_PRIMARY)
          Text('写入本地 JSONL（按日滚动）')
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.colors.TEXT_TERTIARY)
            .margin({ top: 4 })
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        Toggle({ type: ToggleType.Switch, isOn: this.enablePersistence })
          .selectedColor(this.colors.PRIMARY)
          .switchPointColor(this.colors.WHITE)
          .onChange((value: boolean) => {
            this.updatePersistenceEnabled(value);
          })
      }
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

      Row() {
        Column() {
          Text('包含 INFO 级别')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.TEXT_PRIMARY)
          Text('关闭时仅持久化 WARN/ERROR（推荐）')
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.colors.TEXT_TERTIARY)
            .margin({ top: 4 })
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        Toggle({ type: ToggleType.Switch, isOn: this.persistenceIncludeInfo })
          .selectedColor(this.colors.PRIMARY)
          .switchPointColor(this.colors.WHITE)
          .enabled(this.enablePersistence)
          .onChange((value: boolean) => {
            this.updatePersistenceIncludeInfo(value);
          })
      }
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

      Text(`总容量上限：${this.persistenceMaxMB} MB（超限自动删除最旧文件）`)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_SECONDARY)
        .width('100%')
        .margin({ bottom: 8 })

      Row({ space: 8 }) {
        ForEach(this.PERSISTENCE_MB_OPTIONS, (value: number, index: number) => {
          Text(`${value}MB`)
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.persistenceMaxMB === value ? this.colors.WHITE : this.colors.TEXT_PRIMARY)
            .backgroundColor(this.persistenceMaxMB === value ? this.colors.PRIMARY : this.colors.BACKGROUND_SECONDARY)
            .borderRadius(DesignTokens.BorderRadius.FULL)
            .padding({ left: 10, right: 10, top: 6, bottom: 6 })
            .opacity(this.enablePersistence ? 1 : 0.5)
            .onClick(() => {
              if (!this.enablePersistence) {
                return;
              }
              this.updatePersistenceCapacity(index);
            })
        }, (value: number) => String(value))
      }
      .width('100%')
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
    .margin({ bottom: DesignTokens.Spacing.MD })
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
  }

  @Builder
  private buildFilterTabs() {
    Row({ space: DesignTokens.Spacing.SM }) {
      ForEach(this.LEVEL_FILTERS, (filter: LevelFilterOption, index: number) => {
        Text(filter.label)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.selectedLevelIndex === index ? this.colors.WHITE : this.colors.TEXT_PRIMARY)
          .backgroundColor(this.selectedLevelIndex === index ? this.colors.PRIMARY : this.colors.BACKGROUND_SECONDARY)
          .borderRadius(DesignTokens.BorderRadius.FULL)
          .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.MD, top: 4, bottom: 4 })
          .onClick(() => {
            this.selectedLevelIndex = index;
            this.refreshDisplayedLogs();
          })
      }, (filter: LevelFilterOption) => filter.label)
    }
    .width('100%')
    .justifyContent(FlexAlign.Start)
    .padding({ bottom: DesignTokens.Spacing.SM })
  }

  @Builder
  private buildSearchBar() {
    Row() {
      Text('🔍')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .margin({ right: DesignTokens.Spacing.SM })

      TextInput({ placeholder: '搜索日志...', text: this.searchKeyword })
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .placeholderColor(this.colors.TEXT_TERTIARY)
        .backgroundColor(Color.Transparent)
        .layoutWeight(1)
        .height(36)
        .onChange((value: string) => {
          this.searchKeyword = value;
          this.refreshDisplayedLogs();
        })

      if (this.searchKeyword.length > 0) {
        Text('✕')
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.TEXT_TERTIARY)
          .onClick(() => {
            this.searchKeyword = '';
            this.refreshDisplayedLogs();
          })
      }
    }
    .width('100%')
    .height(44)
    .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.MD })
    .backgroundColor(this.colors.BACKGROUND_SECONDARY)
    .borderRadius(DesignTokens.BorderRadius.MD)
    .margin({ bottom: DesignTokens.Spacing.SM })
  }

  @Builder
  private buildLogItem(entry: LogEntry) {
    Column() {
      Row() {
        Text(this.getLevelBadge(entry.level))
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.getLevelColor(entry.level))
          .borderRadius(4)
          .width(18)
          .height(18)
          .textAlign(TextAlign.Center)
          .margin({ right: DesignTokens.Spacing.SM })

        Text(this.formatTimestamp(entry.timestamp))
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.TEXT_TERTIARY)
          .margin({ right: DesignTokens.Spacing.SM })

        if (entry.repeatCount > 1) {
          Text(`x${entry.repeatCount}`)
            .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
            .fontColor(this.colors.WARNING)
            .margin({ right: DesignTokens.Spacing.SM })
        }

        Text(`[${entry.tag}]`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.PRIMARY)
          .fontWeight(FontWeight.Medium)

        Blank()

        Text(entry.message)
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.TEXT_PRIMARY)
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .layoutWeight(1)
          .margin({ left: DesignTokens.Spacing.SM })
      }
      .width('100%')

      if (entry.data && entry.data.length > 0) {
        Text(entry.data)
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.TEXT_SECONDARY)
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .margin({ top: 4, left: 26 })
      }
    }
    .width('100%')
    .padding({ top: 8, bottom: 8 })
  }

  @Builder
  private buildLogList() {
    Column() {
      if (this.displayedLogs.length === 0) {
        Column() {
          Text('暂无日志')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.TEXT_TERTIARY)
        }
        .width('100%')
        .height(300)
        .justifyContent(FlexAlign.Center)
      } else {
        List({ space: 0 }) {
          ForEach(this.displayedLogs, (entry: LogEntry, index: number) => {
            ListItem() {
              this.buildLogItem(entry)
            }
          }, (entry: LogEntry) => `${entry.firstTimestamp}_${entry.timestamp}_${entry.level}_${entry.message}`)
        }
        .width('100%')
        .layoutWeight(1)
        .backgroundColor(this.colors.BACKGROUND_SECONDARY)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .divider({
          strokeWidth: 1,
          color: this.colors.GRAY_100,
          startMargin: 0,
          endMargin: 0
        })
      }
    }
    .width('100%')
    .layoutWeight(1)
  }

  @Builder
  private buildActionButtons() {
    Row() {
      Button(this.isLogExporting ? '导出中...' : '导出日志')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.WHITE)
        .backgroundColor(this.isLogExporting ? this.colors.GRAY_400 : this.colors.PRIMARY)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .height(36)
        .enabled(!this.isLogExporting)
        .onClick(() => { void this.exportLogs(); })

      Blank()

      Button(this.isDiagnosticExporting ? '生成中...' : '诊断报告')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.WHITE)
        .backgroundColor(this.isDiagnosticExporting ? this.colors.GRAY_400 : '#8B5CF6')
        .borderRadius(DesignTokens.BorderRadius.MD)
        .height(36)
        .enabled(!this.isDiagnosticExporting)
        .onClick(() => { void this.exportDiagnostic(); })

      Blank()

      Button('清空')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.WHITE)
        .backgroundColor(this.colors.ERROR)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .height(36)
        .onClick(() => { this.clearLogs(); })
    }
    .width('100%')
    .padding({ top: DesignTokens.Spacing.MD })
  }

  build() {
    Column() {
      this.buildHeader()

      Column() {
        this.buildStatsBar()
        this.buildOutputCard()
        this.buildPersistenceCard()
        this.buildFilterTabs()
        this.buildSearchBar()
        this.buildLogList()
        this.buildActionButtons()

        Text(`缓存上限: ${logger.getMaxCacheSize()} 条 | 预览最近 ${this.PREVIEW_COUNT} 条`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_XS)
          .fontColor(this.colors.TEXT_TERTIARY)
          .width('100%')
          .textAlign(TextAlign.Center)
          .padding({ top: DesignTokens.Spacing.SM })
      }
      .width('100%')
      .layoutWeight(1)
      .padding(DesignTokens.Spacing.MD)
    }
    .width('100%')
    .height('100%')
    .backgroundColor(this.colors.BACKGROUND_PRIMARY)
  }
}
