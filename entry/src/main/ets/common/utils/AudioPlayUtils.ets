import { FileUtil, LogUtil } from '@pura/harmony-utils'
import { EfAVPlayer } from '@yunkss/ef_audio'
import ContinuousTask from './ContinuousTask'
import FileUtils from './FileUtils'
import { fileIo } from '@kit.CoreFileKit'

/**
 * 音频播放工具
 * AudioPlayUtils
 */
const TAG = '[AudioPlayUtils] '

class AudioPlayUtils {
  mPlayer: EfAVPlayer = new EfAVPlayer()
  private isSeeking: boolean = false // seek 完成前忽略 timeUpdate，避免进度回跳到旧位置
  private seekTimer: number = -1

  async init() {
    try {
      await this.mPlayer.init({ immediately: true, loop: false })
      LogUtil.info(TAG + '播放器初始化完成')
    } catch (e) {
      LogUtil.error(TAG + '播放器初始化失败')
      throw new Error(e)
    }
  }

  async playWithUrl(url:string) {
    try {
      await this.init()
      await this.mPlayer.setUrl(url)
      LogUtil.info(TAG + '开始播放: ' + url)
      this.mPlayer.play()
      AppStorage.setOrCreate('player-isplaying',true)
      this.mPlayer.onTimeUpdate((time) => {
        if (!this.isSeeking) { AppStorage.setOrCreate('player-time',time) }
      })
    } catch (e) {
      AppStorage.setOrCreate('player-isplaying',false)
      LogUtil.error(TAG + '播放失败: ' + JSON.stringify(e))
    }
  }

  async playWithFile(fileName:string) {
    try {
      let path = await FileUtils.getFilesDir() + `/${fileName}`
      LogUtil.info(TAG + 'path: ' + path)
      let file = await fileIo.open(path)
      let fdPath = 'fd://' + file.fd
      LogUtil.info(TAG + 'fdPath: ' + fdPath)
      await this.init()
      await this.mPlayer.setUrl(fdPath)
      this.mPlayer.play()
      LogUtil.info(TAG + '开始播放: ' + fileName)
      AppStorage.setOrCreate('player-isplaying',true)
      this.mPlayer.onTimeUpdate((time) => {
        if (!this.isSeeking) { AppStorage.setOrCreate('player-time',time) }
      })
    } catch (e) {
      AppStorage.setOrCreate('player-isplaying',false)
      LogUtil.error(TAG + '播放失败 play error: ' + JSON.stringify(e))
    }
  }

  /**
   * 跳转到指定进度（ms）
   * 立即写入 player-time，seekDone 之前忽略 timeUpdate
   */
  async seek(time: number) {
    AppStorage.setOrCreate('player-time', time)
    const avPlayer = this.mPlayer.getAVPlayer()
    if (!avPlayer) { return }
    this.isSeeking = true
    clearTimeout(this.seekTimer)
    // seekDone 未回调时兜底恢复进度更新
    this.seekTimer = setTimeout(() => { this.isSeeking = false }, 2000)
    avPlayer.off('seekDone')
    avPlayer.on('seekDone', (seekTime: number) => {
      clearTimeout(this.seekTimer)
      this.isSeeking = false
      LogUtil.info(TAG + 'seekDone: ' + seekTime)
    })
    try {
      await this.mPlayer.seek(time)
      LogUtil.info(TAG + '跳转播放: ' + time)
    } catch (e) {
      clearTimeout(this.seekTimer)
      this.isSeeking = false
      LogUtil.error(TAG + '跳转失败: ' + JSON.stringify(e))
    }
  }

  async stop() {
    await this.mPlayer.stop()
    ContinuousTask.stopTask()
    LogUtil.info(TAG + '停止播放')
  }

  async pause() {
    await this.mPlayer.pause()
    LogUtil.info(TAG + '暂停播放')
  }

  async resume() {
    await this.mPlayer.play()
    LogUtil.info(TAG + '继续播放')
  }

}

const audioPlayUtils = new AudioPlayUtils()
export default audioPlayUtils as AudioPlayUtils
