import { LogUtil } from "@pura/harmony-utils"
import { SongDetail } from "../common/entities/SongDetail"
import { QualityType } from "../common/entities/SongDownload"
import { SongPlay } from "../common/entities/SongPlay"
import { SearchSongsData, Song, SongClass, SongsData } from "../common/entities/SongsResult"
import { getApiUrl, isUsePubCookie } from "../common/functions/functions"
import { HttpRequest } from "../common/utils/HttpRequestUtils"

const TAG = '[Song API - songApi] '

export interface SongsListResult {
  hasMore:boolean
  songs:Array<Song>
}

/**
 * 搜素歌曲列表（分页）
 * @param searchKeyword 搜索词
 * @param offset 偏移
 * @returns hasMore 是否还有更多, songs 歌曲列表
 */
export async function getSongsList(searchKeyword:string, offset:number): Promise<SongsListResult> {
  let list:Array<Song> = new Array()
  let hasMore:boolean = false
  const rootUrl = await getApiUrl()
  const url:string = `${rootUrl}/search?keywords=${encodeURIComponent(searchKeyword)}&limit=30&offset=${offset}`
  const request = new HttpRequest(url)
  await request.Request().then((data) => {
    const dataGot:SearchSongsData = data.result as SearchSongsData
    // 接口返回错误码或没有 result 时视为请求失败
    if ((dataGot.code !== undefined && dataGot.code !== 200) || !dataGot.result) {
      throw new Error(TAG + '搜索失败: ' + JSON.stringify(dataGot))
    }
    const songs:Song[] = dataGot.result.songs ?? []
    for(let song of songs) {
      list.push({
        id: song.id,
        name: song.name,
        artists: song.artists,
        duration: song.duration,
      })
    }
    // 只以接口 hasMore 为准；本页为空时不再继续请求
    hasMore = dataGot.result.hasMore === true && list.length > 0
  })
  const result: SongsListResult = {
    hasMore: hasMore,
    songs: list
  }
  return result
}

/**
 * 根据文件名，搜索歌曲信息，返回结果数组的第一个信息
 * @param searchName
 */
export async function getSongInfo(searchName: string): Promise<Song> {
  let song:Song = SongClass
  const rootUrl = await getApiUrl()
  const url:string = `${rootUrl}/search?keywords=${encodeURIComponent(searchName)}`
  const request = new HttpRequest(url)
  await request.Request().then((data) => {
    const dataGot:SongsData = data.result as SongsData
    song = dataGot.result.songs[0]
  })
  return song
}

/**
 * 获取歌曲播放Url
 */
export async function getSongUrl(songId: number, quality:QualityType, isLogged:boolean): Promise<SongPlay> {
  const rootUrl = await getApiUrl()
  const url:string = `${rootUrl}/song/url/v1?id=${songId}&level=${quality}`
  let usePubCookie:boolean = false
  if(isLogged) { usePubCookie = await isUsePubCookie() }
  const request = new HttpRequest(url)
  try {
    const data = usePubCookie ? await request.RequestWithVipType() : await request.Request()
    LogUtil.info(TAG + JSON.stringify(data.result))
    const dataGot: SongPlay = data.result as SongPlay
    return dataGot
  } catch (e) {
    LogUtil.error(TAG + '获取播放url失败: ' + JSON.stringify(e))
    throw new Error(TAG + '获取播放Url失败')
  }
}

/**
 * 获取歌曲图片Url
 * @param song 歌曲类
 * @returns string 歌曲Url
 */
export async function getSongPicUrl(song: Song): Promise<string> {
  const rootUrl = await getApiUrl()
  const url: string = `${rootUrl}/song/detail?ids=${song.id}`;
  const request = new HttpRequest(url);
  try {
    const data = await request.Request();
    const dataGot: SongDetail = data.result as SongDetail;
    const songPicUrl = dataGot.songs[0].al.picUrl;
    return songPicUrl;
  } catch (error) {
    console.error('Error fetching song picUrl:', error);
    return 'NULL';
  }
}