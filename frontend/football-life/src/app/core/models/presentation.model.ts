export enum CareerStatus {
  ACTIVE = 'ACTIVE',
  RETIRED = 'RETIRED'
}

export enum VisualPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum PresentationDensity {
  MINIMAL = 'MINIMAL',
  STANDARD = 'STANDARD',
  DETAILED = 'DETAILED'
}

export interface PresentationSourceReference {
  story_id?: string;
  script_id?: string;
  event_ids: string[];
  milestone_ids: string[];
  turning_point_ids: string[];
  arc_ids: string[];
}

export interface PlayerPresentation {
  player_id: string;
  name: string;
  age?: number;
  nationality?: string;
  position?: string;
  overall_rating?: number;
  current_club?: string;
  market_value_eur?: number;
  salary_eur?: number;
  career_status: CareerStatus;
  primary_archetype?: string;
  image_url?: string;
  source_reference?: PresentationSourceReference;
}

export interface CareerOverview {
  career_start?: string | number;
  career_end?: string | number;
  total_seasons?: number;
  years_active: number;
  clubs_count: number;
  matches: number;
  goals: number;
  assists: number;
  trophies: number;
  trophies_count?: number;
  milestones?: number;
  turning_points?: number;
  peak_rating?: number;
  peak_club?: string;
  career_arc?: string;
}

export interface CareerStatistics {
  matches?: number;
  appearances?: number;
  goals: number;
  assists: number;
  yellow_cards?: number;
  red_cards?: number;
  clean_sheets?: number;
  minutes?: number;
  average_rating?: number;
  trophies: string[];
  awards: string[];
  records?: string[];
}

export interface ClubPresentation {
  club_id: string;
  club_name?: string;
  name?: string;
  period?: string;
  start_year?: number;
  end_year?: number;
  appearances: number;
  goals: number;
  assists: number;
  trophies: string[];
  roles?: string[];
  is_current?: boolean;
}

export interface SeasonPresentation {
  season_id: string;
  year?: number;
  season_name?: string;
  season_label?: string;
  club?: string;
  club_name?: string;
  appearances: number;
  goals: number;
  assists: number;
  average_rating?: number;
  end_overall_rating?: number;
  trophies: string[];
  key_events?: string[];
  important_events?: string[];
}

export interface TimelineEntry {
  entry_id: string;
  timeline_id?: string;
  season?: number;
  date_or_season?: string;
  entry_type: string;
  title: string;
  description?: string;
  summary?: string;
  priority: VisualPriority;
  icon?: string;
  date_label?: string;
  club?: string;
  source_reference?: PresentationSourceReference;
}

export interface CareerHighlight {
  highlight_id: string;
  highlight_type: string;
  title: string;
  description: string;
  season?: number;
  priority: VisualPriority;
  media_url?: string;
  source_reference?: PresentationSourceReference;
}

export interface CareerArcPresentation {
  arc_id: string;
  arc_type: string;
  title?: string;
  description?: string;
  status: string;
  start_year?: number;
  end_year?: number;
  phases?: string[];
}

export interface RelationshipPresentation {
  relationship_id: string;
  target_entity?: string;
  target_entity_name?: string;
  relationship_type: string;
  status: string;
  strength: number;
  description?: string;
}

export interface NarrativePresentation {
  story_id: string;
  title?: string;
  premise: string;
  acts: any[];
  beats: any[];
  climax?: string;
  resolution?: string;
  themes?: string[];
  source_reference?: PresentationSourceReference;
}

export interface ScriptPresentation {
  script_id: string;
  title?: string;
  hook?: any;
  sections: any[];
  climax?: any;
  closing?: any;
  word_count: number;
  estimated_duration_seconds?: number;
  estimated_duration?: number;
  source_reference?: PresentationSourceReference;
}

export interface PresentationMetadata {
  presentation_id: string;
  player_id: string;
  density?: PresentationDensity;
  generated_at_timestamp?: number;
  presentation_version?: string;
}

export interface CareerPresentation {
  presentation_id: string;
  player: PlayerPresentation;
  overview: CareerOverview;
  statistics: CareerStatistics;
  clubs: ClubPresentation[];
  seasons: SeasonPresentation[];
  timeline: TimelineEntry[];
  highlights: CareerHighlight[];
  career_arcs: CareerArcPresentation[];
  relationships: RelationshipPresentation[];
  narrative?: NarrativePresentation;
  script?: ScriptPresentation;
  metadata: PresentationMetadata;
  source_reference?: PresentationSourceReference;
}
