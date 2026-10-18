import { LogUtil } from "@pura/harmony-utils";
import { util } from "@kit.ArkTS";
import { StorageConstants } from "../../constants/StorageConstants";
import { CacheSet, CacheSetItem } from "../../entities/local/Settings";
import { Artist } from "../../entities/song/Song";
import commonRequest from "../../utils/request/RequestUtil";
import { getArtists } from "./convert";

const TAG = '[get function] '
/**
 * 获取API Url
 * （根据用户设置）
 * @returns string - ApiUrl
 */
export async function getApiUrl(): Promise<string | undefined> {
  return AppStorage.get(StorageConstants.API_URL)
}

/**
 * 获取用户Cookie
 * @returns
 */
export async function getCookie(): Promise<string> {
  let cookie = ''
  let isCustomCookie = await AppStorage.get(StorageConstants.IS_CUSTOM_COOKIE) as boolean
  if(isCustomCookie) {
    cookie = await AppStorage.get(StorageConstants.CUSTOM_COOKIE) as string
  } else {
    cookie = await AppStorage.get(StorageConstants.COOKIE) as string
  }
  return cookie
}

interface InnerVersion {
  code: number
}

let checkSeq: number = 0
let checkingKey: string | undefined = undefined
let checkingTask: Promise<boolean> | undefined = undefined

/**
 * 检查API URL连通性
 * 同一配置的检查在途时不重复发请求；配置变化后旧请求的结果作废，不会覆盖新结果
 * @returns
 */
export function checkValidUrl(): Promise<boolean> {
  const apiUrl = AppStorage.get<string>(StorageConstants.API_URL) ?? ''
  const key = `${apiUrl}\n${getApiAuthorization()}`
  if (checkingTask && checkingKey === key) {
    return checkingTask
  }
  const seq = ++checkSeq
  if (!apiUrl) {
    checkingKey = undefined
    checkingTask = undefined
    AppStorage.setOrCreate(StorageConstants.VALID_API_URL, false)
    return Promise.resolve(false)
  }
  checkingKey = key
  const task = requestInnerVersion().then((valid: boolean) => {
    if (seq === checkSeq) {
      AppStorage.setOrCreate(StorageConstants.VALID_API_URL, valid)
      checkingKey = undefined
      checkingTask = undefined
    }
    return valid
  })
  checkingTask = task
  return task
}

async function requestInnerVersion(): Promise<boolean> {
  try {
    const response = await commonRequest<InnerVersion>({
      url: '/inner/version',
      params: {}
    })
    return response.code === 200
  } catch (e) {
    return false
  }
}

/**
 * 在线服务认证头
 * 配置了用户或密码时返回 HTTP Basic 认证值，否则返回 ''
 */
export function getApiAuthorization(): string {
  const user = AppStorage.get<string>(StorageConstants.API_USER) ?? ''
  const password = AppStorage.get<string>(StorageConstants.API_PASSWORD) ?? ''
  if (!user && !password) {
    return ''
  }
  const bytes = new util.TextEncoder().encodeInto(`${user}:${password}`)
  return 'Basic ' + new util.Base64Helper().encodeToStringSync(bytes)
}

export async function getLocalSongArtistsString(localSongArtists: string): Promise<string> {
  let artists: string = localSongArtists
  try {
    const artistsArr: Artist[] = JSON.parse(localSongArtists)
    artists = getArtists(artistsArr)
  } catch (e) {
    LogUtil.warn(TAG + 'getLocalSongArtistString Error')
  }
  return artists
}

export async function getLocalSongArtists(localSongArtists: string): Promise<Artist[]> {
  let artists: Artist[] = [{ id: 0, name: localSongArtists.toString() }]
  try {
    artists = JSON.parse(localSongArtists)
  } catch (e) {
    LogUtil.warn(TAG + 'getLocalSongArtists Error')
  }
  return artists
}

export async function getCacheSet() {
  try {
    const cacheSet = await AppStorage.get(StorageConstants.CACHE_SETTINGS) as CacheSet
    return cacheSet ?? CacheSetItem
  } catch (e) {
    LogUtil.error(TAG, 'getCacheSet Error: ' + e.message)
    return CacheSetItem
  }
}