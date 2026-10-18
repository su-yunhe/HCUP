import { Artist } from "./SongsResult"

/**
 * 私人FM
 */
interface Album {
  picUrl: string
  name: string
}

export interface FMSong {
  id: number
  name: string
  artists: Artist[]
  album: Album
  duration: number
  alias: string[]
  fee: number
}

export interface PersonalFM {
  code: number
  data: FMSong[]
}

/**
 * 私人FM 模式
 * DEFAULT-默认, FAMILIAR-熟悉, EXPLORE-探索
 */
export type FMMode = 'DEFAULT' | 'FAMILIAR' | 'EXPLORE'
