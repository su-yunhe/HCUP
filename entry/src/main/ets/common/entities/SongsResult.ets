export interface Artist {
  id:number
  name:string
}

export interface Song {
  id:number
  name:string
  artists:Artist[]
  duration:number
}

interface Result {
  songs:Song[]
}

export interface SongsData {
  result:Result
}

// 搜索接口分页响应：零结果/超出范围时没有 songs 和 hasMore，异常时没有 result
interface SearchResult {
  songs?:Song[]
  hasMore?:boolean
  songCount?:number
}

export interface SearchSongsData {
  code?:number
  result?:SearchResult
}

export const SongClass: Song = {
  id: 0,
  name: '',
  artists: [
    {
      id: 0,
      name: '',
    }
  ],
  duration: 0
};


export const SongsDataClass: SongsData = {
  result: {
    songs: [
      {
        id: 0,
        name: '',
        artists: [
          {
            id: 0,
            name: '',
          }
        ],
        duration: 0
      }
    ]
  }
};
