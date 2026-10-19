import { SegmentButton, SegmentButtonItemTuple, SegmentButtonOptions } from '@kit.ArkUI';
import { allSymbols, linysSymbol } from '../objects/linysSymbol';
import LinysSymbolDataSource from '../objects/SymbolDataSource';
import { copy } from '../utils/clipboard_tools';

// System preset color with the name shown on its capsule
interface SymbolColor {
  name: string;
  color: Resource;
}

const PRESET_COLORS: SymbolColor[] = [
  { name: 'accent', color: $r('sys.color.ohos_id_color_emphasize') },
  { name: 'connected', color: $r('sys.color.ohos_id_color_connected') },
  { name: 'warning', color: $r('sys.color.ohos_id_color_warning') },
  { name: 'alert', color: $r('sys.color.ohos_id_color_alert') },
  { name: 'handup', color: $r('sys.color.ohos_id_color_handup') },
  { name: 'foreground', color: $r('sys.color.ohos_id_color_foreground') }
];
const DEFAULT_PRIMARY_COLOR: SymbolColor = PRESET_COLORS[0];
const DEFAULT_SECONDARY_COLOR: SymbolColor = PRESET_COLORS[1];

const RENDERING_STRATEGIES: SymbolRenderingStrategy[] = [
  SymbolRenderingStrategy.SINGLE,
  SymbolRenderingStrategy.MULTIPLE_COLOR,
  SymbolRenderingStrategy.MULTIPLE_OPACITY
];
const RENDERING_STRATEGY_NAMES: string[] = ['SINGLE', 'MULTIPLE_COLOR', 'MULTIPLE_OPACITY'];

@Entry
@Component
struct Index {
  // Environment
  @StorageLink('tablet_mode') tablet_mode: boolean = false;
  @StorageLink('screen_width') screen_width: number = 0;
  @StorageLink('screen_height') screen_height: number = 0;
  // UI
  @State inputText: string = "";
  @State symbolTest: Resource = $r('sys.symbol.camera_slash_fill');
  @State selected: linysSymbol = allSymbols[0];
  @State showOperations: boolean = false;
  // Symbol customization
  @State primaryColor: SymbolColor = DEFAULT_PRIMARY_COLOR;
  @State secondaryColor: SymbolColor = DEFAULT_SECONDARY_COLOR;
  @State backgroundLayerColor: SymbolColor | undefined = undefined;
  @State renderingStrategy: SymbolRenderingStrategy = SymbolRenderingStrategy.SINGLE;
  @State @Watch('onStrategySelected') strategyIndexes: number[] = [0];
  @State strategyOptions: SegmentButtonOptions = SegmentButtonOptions.capsule({
    buttons: [
      { text: RENDERING_STRATEGY_NAMES[0] },
      { text: RENDERING_STRATEGY_NAMES[1] },
      { text: RENDERING_STRATEGY_NAMES[2] }
    ] as SegmentButtonItemTuple,
    multiply: false,
    fontSize: 12,
    selectedFontSize: 12
  });
  // Data
  data: LinysSymbolDataSource = new LinysSymbolDataSource(allSymbols);

  build() {
    Column({ space: 10 }) {
      WaterFlow() {
        LazyForEach(this.data, (s: linysSymbol) => {
          LinysSymbolDisplay({
            symbol: s,
            selected: this.selected,
            colors: this.symbolFontColors(),
            renderingStrategy: this.renderingStrategy
          })
        }, (s: linysSymbol) => {
          return s.unicode;
        })
      } // Symbols
      .id('symbol_grid')
      .edgeEffect(EdgeEffect.Spring)
      .width('100%')
      .layoutWeight(1)
      .columnsTemplate("1fr ".repeat(Math.ceil(this.screen_width / 75)))
      .columnsGap(15)
      .rowsGap(15)
      .scrollBar(BarState.On)

      Scroll() {
        Row({ space: 10 }) {
          LinysCapsuleButton({ text: "No. " + this.selected.id.toString(), capsuleId: 'info_no' })
          LinysCapsuleButton({ text: " " + this.selected.char + " ", fontSize: 26, capsuleId: 'info_char' })
          LinysCapsuleButton({ text: this.selected.unicode, capsuleId: 'info_unicode' })
          LinysCapsuleButton({ text: this.selected.name, capsuleId: 'info_name' })
        } // Operations
      }
      .id('info_scroll')
      .width('100%')
      .scrollable(ScrollDirection.Horizontal)
      .scrollBar(BarState.Off)
      .edgeEffect(EdgeEffect.Spring)

      if (this.showOperations) {
        this.OperationsPanel()
      }

      Row({ space: 10 }) {
        TextInput({ text: this.inputText })// Search Blank
          .id('search_input')
          .layoutWeight(1)
          .onChange((newText) => {
            this.inputText = newText;
          })
          .onSubmit(() => {
            this.searchFor(this.inputText);
          })
        SymbolGlyph($r('sys.symbol.arrow_counterclockwise'))// Reset Button
          .id('search_reset')
          .fontColor([$r('app.color.font_color_title')])
          .fontSize(36)
          .onClick(() => {
            this.inputText = '';
            this.searchFor('');
          })
        SymbolGlyph($r('sys.symbol.chevron_up'))// Operations Panel Toggle
          .id('ops_toggle')
          .fontColor([$r('app.color.font_color_title')])
          .fontSize(36)
          .accessibilityText('操作面板')
          .onClick(() => {
            this.showOperations = !this.showOperations;
          })
      }
    }
    .padding({ left: 20, right: 20, top: 10 })
    .height('100%')
    .width('100%')
    .onAreaChange((o, n) => {
      this.on_main_area_change(o, n);
    })
  }

  @Builder
  OperationsPanel() {
    Column({ space: 10 }) {
      Row({ space: 10 }) {
        Column({ space: 8 }) {
          this.ColorPicker('primary', '主色')
          this.ColorPicker('secondary', '副色')
          this.ColorPicker('background', '背景色')
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        SymbolGlyph($r('sys.symbol.arrow_counterclockwise'))// Color Reset Button
          .id('color_reset')
          .fontColor([$r('app.color.font_color_title')])
          .fontSize(36)
          .accessibilityText('重置颜色')
          .onClick(() => {
            this.resetColors();
          })
      } // Color Pickers
      .width('100%')

      Row() {
        SegmentButton({ options: this.strategyOptions, selectedIndexes: $strategyIndexes })
      } // Rendering Strategy
      .id('strategy_segment')
      .width('100%')

      LinysCapsuleButton({
        text: RENDERING_STRATEGY_NAMES[RENDERING_STRATEGIES.indexOf(this.renderingStrategy)],
        fontSize: 16,
        capsuleId: 'strategy_capsule'
      })
    }
    .id('ops_panel')
    .width('100%')
    .alignItems(HorizontalAlign.Start)
  }

  @Builder
  ColorPicker(group: string, label: string) {
    Row({ space: 6 }) {
      Text(label)
        .width(44)
        .fontSize(14)
        .fontColor($r('app.color.font_color_title'))
      Row({ space: 4 }) {
        ForEach(PRESET_COLORS, (c: SymbolColor) => {
          Column()
            .id('color_dot_' + group + '_' + c.name)
            .width(18)
            .height(18)
            .borderRadius(9)
            .backgroundColor(c.color)
            .border({
              width: this.colorOf(group)?.name === c.name ? 3 : 0,
              color: $r('app.color.start_window_background')
            })
            .accessibilityText(c.name)
            .clickEffect({ level: ClickEffectLevel.LIGHT })
            .onClick(() => {
              this.pickColor(group, c);
            })
        }, (c: SymbolColor) => c.name)
      }

      LinysCapsuleButton({
        text: this.colorOf(group)?.name ?? 'undefined',
        fontSize: 14,
        capsuleId: 'color_capsule_' + group
      })
    }
    .id('color_group_' + group)
  }

  // fontColor list of the symbols: primary, secondary, then background if chosen
  symbolFontColors(): ResourceColor[] {
    let colors: ResourceColor[] = [this.primaryColor.color, this.secondaryColor.color];
    if (this.backgroundLayerColor !== undefined) {
      colors.push(this.backgroundLayerColor.color);
    }
    return colors;
  }

  colorOf(group: string): SymbolColor | undefined {
    if (group === 'primary') {
      return this.primaryColor;
    }
    if (group === 'secondary') {
      return this.secondaryColor;
    }
    return this.backgroundLayerColor;
  }

  pickColor(group: string, color: SymbolColor) {
    if (group === 'primary') {
      this.primaryColor = color;
    } else if (group === 'secondary') {
      this.secondaryColor = color;
    } else {
      this.backgroundLayerColor = color;
    }
  }

  resetColors() {
    this.primaryColor = DEFAULT_PRIMARY_COLOR;
    this.secondaryColor = DEFAULT_SECONDARY_COLOR;
    this.backgroundLayerColor = undefined;
  }

  onStrategySelected() {
    const index: number | undefined = this.strategyIndexes[0];
    if (index !== undefined && index >= 0 && index < RENDERING_STRATEGIES.length) {
      this.renderingStrategy = RENDERING_STRATEGIES[index];
    }
  }

  searchFor(key: string) {
    console.log('[Woof]Searching for key: ' + key);
    let searchResult: linysSymbol[] = [];
    for (let index = 0; index < allSymbols.length; index++) {
      const element = allSymbols[index];
      if (element.name.toUpperCase().includes(key.toUpperCase())) {
        searchResult.push(element);
      }
    }
    this.data.setData(searchResult);
  }

  on_main_area_change(_old: Area, n: Area) {
    this.screen_width = n.width as number;
    this.screen_height = n.height as number;
    this.tablet_mode = this.screen_width > 500;
  }
}

@Component
struct LinysSymbolDisplay {
  @Prop symbol: linysSymbol;
  @Link selected: linysSymbol;
  // Colors
  @Prop colors: ResourceColor[] = [$r('app.color.font_color_title')];
  @Prop renderingStrategy: SymbolRenderingStrategy = SymbolRenderingStrategy.SINGLE;
  @Prop fontWeight: FontWeight = FontWeight.Normal;

  build() {
    Column({ space: 10 }) {
      SymbolGlyph($r('sys.symbol.'.concat(this.symbol.name)))
        .fontColor(this.colors)
        .renderingStrategy(this.renderingStrategy)
        .width(50)
        .height(50)
        .fontWeight(this.fontWeight)
        .fontSize(50)
        .clickEffect({ level: ClickEffectLevel.LIGHT })
        .onClick(() => {
          this.selected = this.symbol;
        })
    }

  }
}

@Component
struct LinysCapsuleButton {
  @Prop text: ResourceStr = "   ";
  @Prop fontSize: number = 22;
  @Prop allowCopy: boolean = true;
  @Prop capsuleId: string = "";

  aboutToAppear(): void {
    // Preprocess of text
    this.text = this.text == "" ? "¯\\_(ツ)_/¯" : this.text;
  }

  build() {
    Button(this.text)
      .id(this.capsuleId)
      .type(ButtonType.Capsule)
      .backgroundColor($r('app.color.block_color'))
      .fontColor($r('app.color.font_color_title'))
      .fontSize(this.fontSize)
      .fontWeight(FontWeight.Medium)
      .backgroundColor($r('app.color.block_color'))
      .clickEffect({ level: ClickEffectLevel.LIGHT })
      .onClick(() => {
        if (this.allowCopy && typeof this.text == "string") {
          copy(this.text as string);
        }
      })
  }
}