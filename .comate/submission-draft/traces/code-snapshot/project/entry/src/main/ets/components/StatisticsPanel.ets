import { DesignTokens } from '../model/DesignTokens';

export interface LearningStats {
  totalWords: number;
  mastered: number;
  learning: number;
  newWords: number;
  todayLearned: number;
  todayGoal: number;
  streakDays: number;
}

@Component
export struct StatisticsPanel {
  @Prop stats: LearningStats;
  @State isExpanded: boolean = true;

  build() {
    Column() {
      // Header
      Row() {
        Text('学习统计')
          .fontSize(16)
          .fontWeight(FontWeight.Bold)
          .fontColor(DesignTokens.Colors.GRAY_900)
        
        Blank()

        Text(this.isExpanded ? '收起 ▲' : '展开 ▼')
          .fontSize(12)
          .fontColor(DesignTokens.Colors.PRIMARY)
          .onClick(() => {
            animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
              this.isExpanded = !this.isExpanded;
            })
          })
      }
      .width('100%')
      .padding({ bottom: this.isExpanded ? 16 : 0 })

      if (this.isExpanded) {
        // Main Stats Grid
        Grid() {
          GridItem() { this.buildStatBox('总词数', this.stats.totalWords, DesignTokens.Colors.PRIMARY) }
          GridItem() { this.buildStatBox('已掌握', this.stats.mastered, DesignTokens.Colors.SUCCESS) }
          GridItem() { this.buildStatBox('学习中', this.stats.learning, DesignTokens.Colors.WARNING) }
          GridItem() { this.buildStatBox('未学习', this.stats.newWords, DesignTokens.Colors.TEXT_TERTIARY) }
        }
        .columnsTemplate('1fr 1fr 1fr 1fr')
        .rowsGap(8)
        .columnsGap(8)
        .height(70)
        .width('100%')

        Divider().color(DesignTokens.Colors.BORDER_LIGHT).margin({ top: 16, bottom: 16 })

        // Today & Streak
        Row() {
          // Today
          Column() {
            Text('今日学习')
              .fontSize(12)
              .fontColor(DesignTokens.Colors.GRAY_600)
              .margin({ bottom: 8 })
            
            Row() {
              Text(`${this.stats.todayLearned}`)
                .fontSize(20)
                .fontWeight(FontWeight.Bold)
                .fontColor(DesignTokens.Colors.PRIMARY)
              Text(` / ${this.stats.todayGoal}`)
                .fontSize(14)
                .fontColor(DesignTokens.Colors.GRAY_500)
                .margin({ top: 4 })
            }
          }
          .layoutWeight(1)
          .alignItems(HorizontalAlign.Start)

          Divider().vertical(true).height(40).color(DesignTokens.Colors.BORDER_LIGHT)

          // Streak
          Column() {
            Text('连续学习')
              .fontSize(12)
              .fontColor(DesignTokens.Colors.GRAY_600)
              .margin({ bottom: 8 })
            
            Row() {
              Text('🔥')
                .fontSize(16)
                .margin({ right: 4 })
              Text(`${this.stats.streakDays} 天`)
                .fontSize(20)
                .fontWeight(FontWeight.Bold)
                .fontColor(DesignTokens.Colors.WARNING)
            }
          }
          .layoutWeight(1)
          .alignItems(HorizontalAlign.Center)
        }
        .width('100%')
      }
    }
    .width('100%')
    .padding(16)
    .backgroundColor(DesignTokens.Colors.SURFACE_PRIMARY)
    .borderRadius(16)
    .shadow({ radius: 8, color: DesignTokens.Colors.SHADOW_LIGHT, offsetY: 2 })
  }

  @Builder
  buildStatBox(label: string, value: number, color: ResourceColor) {
    Column() {
      Text(value.toString())
        .fontSize(16)
        .fontWeight(FontWeight.Bold)
        .fontColor(color)
      Text(label)
        .fontSize(12)
        .fontColor(DesignTokens.Colors.GRAY_600)
        .margin({ top: 4 })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor(DesignTokens.Colors.BACKGROUND_SECONDARY)
    .borderRadius(8)
  }
}
