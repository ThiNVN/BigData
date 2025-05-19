export interface GameActionProps {
  type: "game-detail";
  payload: GameProps;
}

export interface GameResponseProps {
  games: GameProps[];
}

export interface GameProps {
  rank: number;
  score: number;
  app_id: number;
  name: string;
  type: string;
  required_age: number;
  is_free: boolean;
  supported_languages: string[];
  developers: string;
  publishers: string;
  price_final: number;
  platforms_windows: boolean;
  platforms_mac: boolean;
  platforms_linux: boolean;
  categories: string;
  genres: string;
  recommendations_total: string;
  release_date: string;
  price_currency: string;
  metacritic_score: string;
  short_description: string;
  detailed_description: string;
  about_the_game: string;
  website: string;
  discount_percent: string;
  pc_min_os: string;
  pc_min_processor: string;
  pc_min_memory: string;
  pc_min_graphics: string;
  pc_min_directx: string;
  pc_min_network: string;
  pc_min_storage: string;
  header_image: string;
  background: string;
  screenshots_count: string;
  movies_count: string;
  pc_rec_os: string;
  pc_rec_processor: string;
  pc_rec_memory: string;
  pc_rec_graphics: string;
  support_email: string;
  pc_rec_directx: string;
  pc_rec_network: string;
  pc_rec_storage: string;
}
