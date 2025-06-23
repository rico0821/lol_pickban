export interface Champion {
  id: string;
  key: string;
  name: string;
  title: string;
  image: {
    full: string;
    sprite: string;
    group: string;
    x: number;
    y: number;
    w: number;
    h: number;
  };
  blurb: string;
}

export interface ChampionData {
  type: string;
  format: string;
  version: string;
  data: {
    [key: string]: Champion;
  };
} 