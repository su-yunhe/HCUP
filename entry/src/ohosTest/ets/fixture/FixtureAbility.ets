import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from "@kit.AbilityKit";
import { window } from "@kit.ArkUI";
import { IBestUIInitializer } from "ibestui";
import { ContextUtil } from "util";

/** Test source set only. No main EntryAbility or route graph is changed. */
export default class FixtureAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    try {
      ContextUtil.init(this.context);
      this.context.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET);
    } catch (error) { console.error("[CML24FixtureControl] ability initialization failed"); }
  }

  onWindowStageCreate(stage: window.WindowStage): void {
    try {
      stage.loadContent("pages/GoodsCategoryFixturePage", (): void => {
        IBestUIInitializer.initIBestUI(stage, this.context);
      });
    } catch (error) { console.error("[CML24FixtureControl] fixture page load failed"); }
  }
}
