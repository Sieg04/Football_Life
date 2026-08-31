import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { CareerPresentation, CareerStatus } from '../models/presentation.model';

export enum CareerSessionStatus {
  SETUP = 'SETUP',
  ACTIVE = 'ACTIVE',
  EVENT_PENDING = 'EVENT_PENDING',
  DECISION_PENDING = 'DECISION_PENDING',
  PAUSED = 'PAUSED',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export interface DecisionOption {
  id: string;
  label: string;
  description: string;
  weight?: number;
  available?: boolean;
}

export interface Decision {
  id: string;
  prompt: string;
  options: DecisionOption[];
  default_option_id?: string;
  metadata?: Record<string, any>;
}

export interface CareerSessionNotification {
  id: string;
  title: string;
  message: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  created_at_season: string;
}

export interface CareerSession {
  career_id: string;
  player_id: string;
  current_season: string;
  simulation_position: number;
  status: CareerSessionStatus;
  career: any;
  career_record: any;
  presentation: CareerPresentation;
  pending_decision?: Decision | null;
  pending_events?: any[];
  notifications?: CareerSessionNotification[];
  last_processed_event_id?: string | null;
  seed: string;
}

export interface CareerAdvanceResult {
  career_id: string;
  previous_season: string;
  current_season: string;
  status: CareerSessionStatus;
  processed_events: any[];
  new_notifications: CareerSessionNotification[];
  pending_decision?: Decision | null;
  presentation?: CareerPresentation | null;
  season_summary?: any;
  success: boolean;
}

export interface CareerSetupRequest {
  player_name: string;
  position?: string;
  starting_club_id?: string;
  nationality?: string;
  seed?: string;
}

// Fallback session helper
function createFallbackSession(name: string, pos: string, club: string): CareerSession {
  return {
    career_id: 'cs_fallback_001',
    player_id: 'p_fallback_001',
    current_season: '2026/27',
    simulation_position: 1,
    status: CareerSessionStatus.ACTIVE,
    career: { current_season_number: 1 },
    career_record: { events: [] },
    presentation: {
      presentation_id: 'pres_fallback_001',
      player: {
        player_id: 'p_fallback_001',
        name: name || 'Adrian Martínez',
        age: 21,
        nationality: 'Spain',
        position: pos || 'ST',
        overall_rating: 75,
        current_club: club || 'FC Barcelona',
        market_value_eur: 15000000,
        salary_eur: 45000,
        career_status: CareerStatus.ACTIVE
      },
      overview: {
        years_active: 1,
        clubs_count: 1,
        matches: 28,
        goals: 12,
        assists: 5,
        trophies: 0,
        trophies_count: 0,
        milestones: 1,
        turning_points: 0,
        peak_rating: 75
      },
      statistics: {
        matches: 28,
        goals: 12,
        assists: 4,
        average_rating: 7.2,
        trophies: [],
        awards: []
      },
      clubs: [],
      seasons: [],
      timeline: [],
      highlights: [],
      career_arcs: [],
      relationships: [],
      metadata: { presentation_id: 'pres_fallback_001', player_id: 'p_fallback_001' }
    },
    pending_decision: null,
    pending_events: [],
    notifications: [
      {
        id: 'notif_welcome',
        title: 'Career Created',
        message: `Welcome to Football Life! ${name} has started his professional career.`,
        type: 'INFO',
        created_at_season: '2026/27'
      }
    ],
    seed: 'FL-CAREER-0001'
  };
}

@Injectable({
  providedIn: 'root'
})
export class CareerSessionService {
  private apiUrl = 'http://localhost:8000/career';

  private activeSessionSubject = new BehaviorSubject<CareerSession | null>(null);
  public activeSession$ = this.activeSessionSubject.asObservable();

  private recordingModeSubject = new BehaviorSubject<boolean>(false);
  public recordingMode$ = this.recordingModeSubject.asObservable();

  constructor(private http: HttpClient) {}

  public get currentSession(): CareerSession | null {
    return this.activeSessionSubject.value;
  }

  public toggleRecordingMode(): void {
    this.recordingModeSubject.next(!this.recordingModeSubject.value);
  }

  public setRecordingMode(active: boolean): void {
    this.recordingModeSubject.next(active);
  }

  createCareer(request: CareerSetupRequest): Observable<CareerSession> {
    return this.http.post<CareerSession>(this.apiUrl, request).pipe(
      tap((session) => this.activeSessionSubject.next(session)),
      catchError(() => {
        const fallback = createFallbackSession(
          request.player_name,
          request.position || 'ST',
          request.starting_club_id || 'FC Barcelona'
        );
        this.activeSessionSubject.next(fallback);
        return of(fallback);
      })
    );
  }

  getCareerSession(careerId: string): Observable<CareerSession> {
    return this.http.get<CareerSession>(`${this.apiUrl}/${careerId}`).pipe(
      tap((session) => this.activeSessionSubject.next(session)),
      catchError(() => {
        const fallback = createFallbackSession('Adrian Martínez', 'ST', 'FC Barcelona');
        this.activeSessionSubject.next(fallback);
        return of(fallback);
      })
    );
  }

  advanceCareer(careerId: string): Observable<CareerAdvanceResult> {
    return this.http.post<CareerAdvanceResult>(`${this.apiUrl}/${careerId}/advance`, {}).pipe(
      tap((result) => {
        const current = this.activeSessionSubject.value;
        if (current) {
          const updated: CareerSession = {
            ...current,
            current_season: result.current_season,
            simulation_position: current.simulation_position + 1,
            status: result.status,
            presentation: result.presentation || current.presentation,
            pending_decision: result.pending_decision || null,
            notifications: [...(current.notifications || []), ...(result.new_notifications || [])]
          };
          this.activeSessionSubject.next(updated);
        }
      })
    );
  }

  resolveDecision(careerId: string, decisionId: string, optionId: string): Observable<CareerSession> {
    return this.http
      .post<CareerSession>(`${this.apiUrl}/${careerId}/decision`, {
        decision_id: decisionId,
        option_id: optionId
      })
      .pipe(
        tap((session) => this.activeSessionSubject.next(session))
      );
  }

  resolveTransfer(careerId: string, offerId: string, action: string): Observable<CareerSession> {
    return this.http
      .post<CareerSession>(`${this.apiUrl}/${careerId}/transfer`, {
        offer_id: offerId,
        action: action
      })
      .pipe(
        tap((session) => this.activeSessionSubject.next(session))
      );
  }

  pauseCareer(careerId: string): Observable<CareerSession> {
    return this.http.post<CareerSession>(`${this.apiUrl}/${careerId}/pause`, {}).pipe(
      tap((session) => this.activeSessionSubject.next(session))
    );
  }
}
