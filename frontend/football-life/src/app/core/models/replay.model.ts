export interface ReplayMoment {
  moment_id: string;
  moment_type: string;
  title: string;
  description: string;
  priority: string;
  season_id?: string;
  season_number?: number;
  day_number?: number;
  impact_score?: number;
  visual_priority?: string;
  tags?: string[];
  payload?: Record<string, any>;
}

export interface ReplaySeason {
  season_id?: string;
  season_number?: number;
  year?: number;
  club_name?: string;
  moments: ReplayMoment[];
}

export interface CareerReplay {
  career_id: string;
  player_name: string;
  created_at?: string;
  total_seasons: number;
  total_moments: number;
  seasons: ReplaySeason[];
  moments: ReplayMoment[];
}

export interface ContentScene {
  scene_id: string;
  scene_type: string;
  title: string;
  subtitle?: string | null;
  headline?: string | null;
  description?: string | null;
  body_text?: string | null;
  stat_highlights: Array<[string, string]>;
  priority: string;
  duration_seconds: number;
  layout_preset: string;
  source_moment_ids?: string[];
  metadata?: Record<string, any>;
}

export interface ContentStory {
  story_id: string;
  career_id: string;
  title: string;
  total_scenes: number;
  estimated_duration_seconds: number;
  scenes: ContentScene[];
  created_at?: string;
  metadata?: Record<string, any>;
}

export interface CapturePreset {
  preset_id: string;
  width: number;
  height: number;
  aspect_ratio: string;
  show_brand_watermark?: boolean;
  show_branding?: boolean;
  theme?: string;
}

export interface CaptureFrame {
  scene: ContentScene;
  preset: CapturePreset;
  rendered_at?: string;
  frame_hash: string;
}
