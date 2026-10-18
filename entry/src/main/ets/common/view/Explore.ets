import { DialogUtil, LogUtil, ToastUtil} from "@pura/harmony-utils";
import Constants from "../constants/Constants";
import { TopListItem } from "../entities/recommend/TopList";
import { getTopList } from "../../api/topListApi";
import { TopListItemCard } from "../../components/cards/TopListItemCard";
import { StorageConstants } from "../constants/StorageConstants";
import { getPersonalizedList } from "../../api/playListApi";
import { PersonalListItem } from "../entities/recommend/Personalized";
import { PersonalizedCard } from "../../components/cards/PersonalizedCard";
import { AppInfo, AppInfoClass } from "../entities/local/AppInfo";
import { RecommendDjRadio } from "../entities/dj/DjRecommend";
import { IndexRecommend } from "./IndexRecommend";
import { PersonalizedSkeletion } from "../../components/skeleton/Skeleton";
import { ApiConfigForm } from "../../components/settings/ApiConfigForm";

const TAG = '[Explore] '

@Component
export struct Explore {
  @StorageProp('bottomRectHeight') bottomRectHeight: number = 0
  @StorageProp('topRectHeight') topRectHeight: number = 0
  @StorageProp(StorageConstants.IS_LOGGED) @Watch('getContent') isLogged: boolean = false
  @StorageProp(StorageConstants.VALID_API_URL) @Watch('onValidApiUrlChange') validApiUrl: boolean = true
  @StorageProp(StorageConstants.APP_LOADING) @Watch('onAppLoadingChange') appLoading: boolean = true
  @StorageProp(StorageConstants.APP_INFO) appInfo: AppInfo = AppInfoClass
  @StorageLink(StorageConstants.TOPLISTS) topList: Array<TopListItem> = []
  @StorageLink(StorageConstants.PERSONALIZED_LIST) personalizedList: Array<PersonalListItem> = []
  @StorageLink(StorageConstants.RECOMMENDED_DJ) recommendDjRadioList: Array<RecommendDjRadio> = []
  @StorageProp(StorageConstants.BREAKPOINT_WIDTH) breakpoint: string = 'sm'
  @State isLoadingTopList: boolean = false
  @State isLoadingPersonalized: boolean = false
  @State isLoadingRecommendDjRadio: boolean = false
  @State isRefreshing: boolean = false
  @State lastRefreshTime: number = 0
  @State isShowApiSheet: boolean = false
  @Prop currentHour: number = 0
  @State totalOpacity: number = 0
  @Consume('pageInfos') pageInfos: NavPathStack
  private refreshCooldown: number = 5000
  private isOnlineContentLoaded: boolean = false
  private apiSheetOptions: SheetOptions = {
    preferType: SheetType.BOTTOM,
    // 内容从顶部排布，软键盘弹出时"保存配置"不被遮挡
    height: SheetSize.LARGE,
    title: { title: '在线服务配置' },
    backgroundColor: $r('app.color.background'),
    // 关闭动画开始前即复位，关闭过程中再次点击"设置在线服务"也能重新弹出
    onWillDisappear: () => { this.isShowApiSheet = false }
  }

  aboutToAppear() {
    animateTo({ duration: 300, curve: Curve.Ease, delay: 100}, () => {
      this.totalOpacity = 1
    })
    // 应用初始化（连通性检查）已完成后才创建的情况
    if(!this.appLoading && this.validApiUrl) {
      this.loadOnlineContent()
    }
  }

  async getContent() {
    this.getTopLists()
    this.getPersonalizedList()
  }

  // 在线服务变为可用（保存配置检查通过）后刷新在线内容
  onValidApiUrlChange() {
    if(this.validApiUrl) {
      this.loadOnlineContent()
    } else {
      this.isOnlineContentLoaded = false
    }
  }

  // 冷启动连通性检查完成后加载在线内容（不要求登录）
  onAppLoadingChange() {
    if(!this.appLoading && this.validApiUrl) {
      this.loadOnlineContent()
    }
  }

  /**
   * 加载在线内容（不受本地缓存、登录态和刷新冷却影响）
   * 每次在线服务变为可用后只加载一次
   */
  private async loadOnlineContent() {
    if(!this.validApiUrl || this.isOnlineContentLoaded) return
    this.isOnlineContentLoaded = true
    await Promise.all([this.loadTopList(), this.loadPersonalizedList()])
  }

  private async loadTopList() {
    if(this.isLoadingTopList) return
    this.isLoadingTopList = true
    try {
      this.topList = (await getTopList()) ?? []
    } catch (e) {
      LogUtil.error(TAG, 'getTopList Error: ' + e.message)
    } finally {
      this.isLoadingTopList = false
    }
  }

  private async loadPersonalizedList() {
    if(this.isLoadingPersonalized) return
    this.isLoadingPersonalized = true
    try {
      this.personalizedList = (await getPersonalizedList()) ?? []
    } catch (e) {
      LogUtil.error(TAG, 'getPersonalizedList Error: ' + e.message)
    } finally {
      this.isLoadingPersonalized = false
    }
  }

  private async getTopLists() {
    if(this.topList.length == 0 && this.validApiUrl) {
      await this.loadTopList()
    }
    else return
  }

  private async getPersonalizedList() {
    if(this.isLogged && this.personalizedList.length == 0 && this.validApiUrl) {
      await this.loadPersonalizedList()
    }
    else return
  }

  private refreshContent = async () => {
    this.isRefreshing = true
    // 在线服务不可用时不请求内容
    if(!this.validApiUrl) {
      setTimeout(() => { this.isRefreshing = false }, 300)
      return
    }
    const currentTime = new Date().getTime()
    if (currentTime - this.lastRefreshTime < this.refreshCooldown) {
      ToastUtil.showToast('操作过于频繁，请5秒后再试')
    } else {
      try {
        Promise.all([
          this.topList = await getTopList(),
          this.personalizedList = await getPersonalizedList(),
        ])
        this.lastRefreshTime = currentTime
        ToastUtil.showToast('刷新成功')
      } catch (e) {
        ToastUtil.showToast('内容刷新失败: ' + e.message)
      }
    }
    this.isRefreshing = false
  }

  build() {
    Column() {
      Refresh({ refreshing: this.isRefreshing }) {
        Grid() {
          if(this.appInfo.data.Announcement.isShow) {
            GridItem() {
              this.Announcement()
            }
          }
          GridItem() {
            Search({
              placeholder: $r('app.string.Search_content'),
              icon: '/resources/base/media/ic_public_search_filled.svg',
            })
              .clickEffect({ level: ClickEffectLevel.LIGHT, scale: 0.9 })
              .focusable(false)
              .onClick(() => {
                this.pageInfos.clear()
                this.pageInfos.pushPathByName('SearchPage', null, this.breakpoint === 'lg' && this.pageInfos.size() === 0 ? false : true)
              })
              .layoutWeight(1)
          }
          .padding({ left: 20, right: 20 })

          GridItem() {
            Column({ space: 5 }) {
              this.Intro(this.getGreeting(this.currentHour), () => {})
              IndexRecommend({ isLogged: this.isLogged })
            }
          }

          if(this.validApiUrl) {
            GridItem() {
              Column({ space: 5 }) {
                this.Intro('推荐歌单', () => {})
                // 推荐歌单
                List() {
                  ListItem().width(5)
                  ListItem().width(5)
                  if(this.isLoadingPersonalized || this.isRefreshing) {
                    ForEach(Constants.ARRAY_LENGTH_10, (item: number) => {
                      PersonalizedSkeletion()
                    })
                  } else {
                    ForEach(this.personalizedList, (item: PersonalListItem, index) => {
                      PersonalizedCard({ item: item }).padding(5)
                    }, (item: PersonalListItem) => item.id.toString())
                  }
                  ListItem().width(5)
                  ListItem().width(5)
                }
                .lanes(2)
                .listDirection(Axis.Horizontal)
                .scrollBar(BarState.Off)
                .width('100%')
                .id('explore_personalized_list')
              }
            }
            .padding({ top: 20 })

            // GridItem() {
            //   Column({ space: 5 }) {
            //     this.Intro('推荐电台', () => {})
            //     // 推荐歌单
            //     List() {
            //       ListItem().width(5)
            //       ListItem().width(5)
            //       ForEach(this.recommendDjRadioList, (item: RecommendDjRadio) => {
            //         ListItem() {
            //           DjRadioRecommendCard({ djRadio: item }).padding(10)
            //         }
            //       }, (item: PersonalListItem) => item.id.toString())
            //       ListItem().width(5)
            //       ListItem().width(5)
            //     }
            //     .listDirection(Axis.Horizontal)
            //     .scrollBar(BarState.Off)
            //     .width('100%')
            //   }
            // }
            // .padding({ top: 20 })

            GridItem() {
              Column({ space: 15 }) {
                this.Intro('排行榜', () => {
                  this.pageInfos.pushPathByName('TopListPage', null, this.breakpoint === 'lg' && this.pageInfos.size() === 0 ? false : true)
                })
                // 排行榜
                List() {
                  ListItem().width(15)
                  ForEach(this.topList.slice(0, 10), (item: TopListItem) => {
                    ListItem() {
                      TopListItemCard({ topListItem: item, breakpoint: this.breakpoint }).padding(5)
                    }
                  })
                  ListItem() {
                    Button() {
                      Column({ space: 5 }) {
                        Stack({ alignContent: Alignment.Center }) {
                          Image($r('app.media.bg4'))
                            .width(120)
                            .aspectRatio(1)
                            .borderRadius(Constants.RADIUS_CARD)
                            .draggable(false)
                          Text('更多排行')
                            .fontSize(Constants.FONT_SIZE_COMMON + 3)
                            .fontWeight(FontWeight.Bold)
                            .fontColor(Color.White)
                        }
                        .width(120)
                        .aspectRatio(1)
                        .backgroundColor(Color.Transparent)
                      }
                    }
                    .backgroundColor(Color.Transparent)
                    .borderRadius(Constants.RADIUS_CARD)
                    .type(ButtonType.Normal)
                    .width(120)
                    .aspectRatio(1)
                    .clickEffect({ level: ClickEffectLevel.LIGHT, scale: 0.9 })
                    .onClick(() => { this.pageInfos.pushPathByName('TopListPage', null, this.breakpoint === 'lg' && this.pageInfos.size() === 0 ? false : true) })
                  }.padding(5)
                  ListItem().width(15)
                }
                .listDirection(Axis.Horizontal)
                .scrollBar(BarState.Off)
                .width('100%')
                .height('auto')
                .id('explore_toplist_list')
              }
            }
            .padding({ top: 20 })
          } else {
            // 在线服务未配置/不可用时的引导
            GridItem() {
              Column({ space: 15 }) {
                Text('如需连接在线内容，请设置在线服务')
                  .id('explore_service_tip')
                  .fontSize(Constants.FONT_SIZE_COMMON)
                  .fontColor($r('app.color.reverse'))
                  .textAlign(TextAlign.Center)
                Button('设置在线服务')
                  .id('explore_setup_button')
                  .fontSize(Constants.FONT_SIZE_COMMON)
                  .fontColor($r('app.color.app_red'))
                  .borderColor($r('app.color.app_red'))
                  .backgroundColor(Color.Transparent)
                  .borderWidth(1)
                  .padding({ left: 20, right: 20 })
                  .onClick(() => {
                    this.isShowApiSheet = true
                  })
              }
              .width('100%')
              .padding({ left: 20, right: 20, top: 20 })
            }
          }

          GridItem()
            .height(px2vp(this.bottomRectHeight) + 115)
        }
        .height('100%')
        .width('100%')
        .edgeEffect(EdgeEffect.Spring)
        .scrollBar(BarState.Off)
        .rowsGap(15)
        .columnsTemplate('1fr')
        .layoutDirection(GridDirection.Column)
        .expandSafeArea([SafeAreaType.SYSTEM], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM])
        .backToTop(true)
      }
      .expandSafeArea([SafeAreaType.SYSTEM], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM])
      .onRefreshing(this.refreshContent)
    }
    .width('100%')
    .height('100%')
    .opacity(this.totalOpacity)
    .bindSheet(this.isShowApiSheet, this.ApiSheet(), this.apiSheetOptions)
  }

  @Builder
  ApiSheet() {
    Scroll() {
      Column() {
        ApiConfigForm({
          onSaved: () => {
            this.isShowApiSheet = false
          }
        })
      }
      .padding({ left: 20, right: 20, bottom: 20 })
    }
    .id('explore_api_sheet')
    .width('100%')
    .height('100%')
    .align(Alignment.Top)
    .scrollBar(BarState.Off)
  }

  @Builder
  Loading(ht: number | string = '100%') {
    Column() {
      LoadingProgress().width(Constants.SIZE_LOADING_PROGRESS_DEFAULT)
    }
    .height(ht)
    .padding({ bottom: px2vp(this.topRectHeight) + 60 })
    .width('100%')
    .justifyContent(FlexAlign.Center)
  }

  @Builder
  Announcement() {
    Row() {
      Text(this.appInfo.data.Announcement.message)
        .width('100%')
        .textAlign(TextAlign.Center)
        .fontColor($r('app.color.main'))
        .fontSize(Constants.FONT_SIZE_COMMON)
        .padding({ top: 5, bottom: 5 })
        .layoutWeight(1)
        .textOverflow({ overflow: TextOverflow.MARQUEE })
        .onClick(() => {
          DialogUtil.showConfirmDialog({
            title: this.appInfo.data.Announcement.title,
            message: this.appInfo.data.Announcement.message
          })
        })
    }
    .backgroundColor('#fff8b8b8')
  }

  @Builder Intro(title: string, action: () => void) {
    Row({ space: 5 }) {
      Text(title)
        .textStyle(18)
      Image($r('app.media.ic_public_arrow_right'))
        .width(Constants.SIZE_ICON_BUTTON_BAR)
        .fillColor($r('app.color.reverse'))
    }
    .width('100%')
    .justifyContent(FlexAlign.Start)
    .clickEffect({ level: ClickEffectLevel.LIGHT, scale: 0.9 })
    .onClick(action)
  }

  private getGreeting(hour: number): string {
    if (hour >= 5 && hour < 7) return '清晨好'
    if (hour >= 7 && hour < 9) return '早上好'
    if (hour >= 9 && hour < 11) return '上午好'
    if (hour >= 11 && hour < 13) return '中午好'
    if (hour >= 13 && hour < 18) return '下午好'
    if (hour >= 18 && hour < 24) return '晚上好'
    if (hour >= 0 && hour < 5) return '夜已深, 注意休息'
    return '探索您喜爱的内容'
  }
}

@Extend(Text) function textStyle(size: number) {
  .fontSize(size)
  .fontWeight(FontWeight.Bold)
  .fontColor($r('app.color.reverse'))
  .padding({ left: 20 })
}