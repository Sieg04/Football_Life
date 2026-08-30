import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CareerPresentation, CareerStatus, VisualPriority, PresentationDensity } from '../models/presentation.model';

@Injectable({
  providedIn: 'root'
})
export class CareerPresentationService {
  private apiUrl = 'http://localhost:8000/presentation';

  constructor(private http: HttpClient) {}

  getPresentation(playerId?: string): Observable<CareerPresentation> {
    const url = playerId ? `${this.apiUrl}/${playerId}` : `${this.apiUrl}/sample`;
    return this.http.get<CareerPresentation>(url).pipe(
      catchError(() => of(this.getFallbackPresentation(playerId || 'player_7')))
    );
  }

  getFallbackPresentation(playerId: string = 'player_7'): CareerPresentation {
    return {
      presentation_id: `pres_${playerId}`,
      player: {
        player_id: playerId,
        name: 'Adrian Martínez',
        age: 24,
        nationality: 'Spain',
        position: 'CF',
        overall_rating: 87,
        current_club: 'FC Barcelona',
        market_value_eur: 74000000,
        salary_eur: 180000,
        career_status: CareerStatus.ACTIVE,
        primary_archetype: 'Clinical Finisher'
      },
      overview: {
        years_active: 6,
        clubs_count: 2,
        matches: 182,
        goals: 96,
        assists: 41,
        trophies: 4,
        trophies_count: 4,
        milestones: 5,
        turning_points: 3,
        peak_rating: 87
      },
      statistics: {
        matches: 182,
        goals: 96,
        assists: 41,
        yellow_cards: 12,
        red_cards: 1,
        average_rating: 7.8,
        trophies: ['La Liga Title (2028)', 'UEFA Champions League (2030)', 'Copa del Rey (2029, 2031)'],
        awards: ['La Liga Golden Boot (2030)', 'Young Player of the Season (2027)'],
        records: ['Youngest hat-trick scorer in club history (2027)']
      },
      clubs: [
        {
          club_id: 'club_01',
          name: 'FC Barcelona Academy',
          club_name: 'FC Barcelona Academy',
          period: '2024 - 2026',
          start_year: 2024,
          end_year: 2026,
          appearances: 35,
          goals: 22,
          assists: 10,
          trophies: ['Youth League Champion'],
          roles: ['Prospect'],
          is_current: false
        },
        {
          club_id: 'club_02',
          name: 'FC Barcelona',
          club_name: 'FC Barcelona',
          period: '2026 - Present',
          start_year: 2026,
          appearances: 147,
          goals: 74,
          assists: 31,
          trophies: ['La Liga (2028)', 'UEFA Champions League (2030)', 'Copa del Rey (2029, 2031)'],
          roles: ['Key Forward'],
          is_current: true
        }
      ],
      seasons: [
        {
          season_id: 's_2026',
          year: 2026,
          season_name: '2026/27',
          club: 'FC Barcelona',
          appearances: 28,
          goals: 12,
          assists: 5,
          average_rating: 7.4,
          end_overall_rating: 76,
          trophies: [],
          key_events: ['First Team Debut', 'Breakthrough Goal']
        },
        {
          season_id: 's_2027',
          year: 2027,
          season_name: '2027/28',
          club: 'FC Barcelona',
          appearances: 34,
          goals: 18,
          assists: 8,
          average_rating: 7.7,
          end_overall_rating: 80,
          trophies: ['La Liga'],
          key_events: ['First Senior Trophy']
        },
        {
          season_id: 's_2030',
          year: 2030,
          season_name: '2030/31',
          club: 'FC Barcelona',
          appearances: 42,
          goals: 31,
          assists: 12,
          average_rating: 8.3,
          end_overall_rating: 87,
          trophies: ['UEFA Champions League'],
          key_events: ['Champions League Winner', 'Golden Boot']
        }
      ],
      timeline: [
        {
          entry_id: 'tl_1',
          season: 2024,
          entry_type: 'ACADEMY',
          title: 'Promoted to La Masia Youth Team',
          description: 'Entered FC Barcelona youth academy system with exceptional promise.',
          summary: 'Entered FC Barcelona youth academy system.',
          priority: VisualPriority.MEDIUM,
          icon: '⚽',
          date_label: '2024',
          club: 'FC Barcelona Academy'
        },
        {
          entry_id: 'tl_2',
          season: 2026,
          entry_type: 'DEBUT',
          title: 'First Team Debut',
          description: 'Made senior debut in La Liga and scored a remarkable volley.',
          summary: 'Made senior debut in La Liga.',
          priority: VisualPriority.HIGH,
          icon: '★',
          date_label: '2026',
          club: 'FC Barcelona'
        },
        {
          entry_id: 'tl_3',
          season: 2028,
          entry_type: 'BREAKTHROUGH',
          title: 'First Senior League Title',
          description: 'Secured the first major senior league trophy as a key contributor.',
          summary: 'Secured the first major senior league trophy.',
          priority: VisualPriority.CRITICAL,
          icon: '🏆',
          date_label: '2028',
          club: 'FC Barcelona'
        },
        {
          entry_id: 'tl_4',
          season: 2030,
          entry_type: 'ACHIEVEMENT',
          title: 'Champions League Triumph & Golden Boot',
          description: 'Led the tournament scoring table and lifted the European cup.',
          summary: 'Led the tournament scoring table.',
          priority: VisualPriority.CRITICAL,
          icon: '🏆',
          date_label: '2030',
          club: 'FC Barcelona'
        }
      ],
      highlights: [
        {
          highlight_id: 'hl_1',
          highlight_type: 'BREAKTHROUGH',
          title: 'Breakthrough Season',
          description: 'Established as first choice striker at age 21.',
          season: 2027,
          priority: VisualPriority.HIGH
        },
        {
          highlight_id: 'hl_2',
          highlight_type: 'TROPHY',
          title: 'Champions League Glory',
          description: 'Scored two goals in the final victory.',
          season: 2030,
          priority: VisualPriority.CRITICAL
        }
      ],
      career_arcs: [
        {
          arc_id: 'arc_1',
          arc_type: 'BREAKTHROUGH',
          title: 'The Academy Prodigy',
          description: 'Rapid ascension from academy ranks into starting lineup.',
          status: 'COMPLETED',
          start_year: 2024,
          end_year: 2027
        },
        {
          arc_id: 'arc_2',
          arc_type: 'PEAK',
          title: 'European Dominance',
          description: 'Established amongst world football top goalscorers.',
          status: 'ACTIVE',
          start_year: 2028
        }
      ],
      relationships: [
        {
          relationship_id: 'rel_1',
          target_entity: 'Manager Xavier',
          relationship_type: 'MENTOR',
          status: 'ACTIVE',
          strength: 0.92,
          description: 'Trusted tactic manager who gave him first team debut.'
        },
        {
          relationship_id: 'rel_2',
          target_entity: 'Lucas Vance',
          relationship_type: 'TEAMMATE',
          status: 'ACTIVE',
          strength: 0.88,
          description: 'Primary attacking partner and assist provider.'
        }
      ],
      narrative: {
        story_id: 'story_01',
        title: 'THE RISE: FROM ACADEMY TO EUROPEAN CHAMPION',
        premise: 'A generational striker overcomes early doubts to lead his childhood club to European glory.',
        acts: [
          { act_id: 'act_1', title: 'Act I: The Academy Spark', description: 'Early potential shown at youth levels.' },
          { act_id: 'act_2', title: 'Act II: Stepping into Light', description: 'Making senior impact under pressure.' },
          { act_id: 'act_3', title: 'Act III: Apex of Europe', description: 'Reaching peak European dominance.' }
        ],
        beats: [
          { beat_id: 'beat_1', beat_type: 'DEBUT', text: 'First senior appearance before 50,000 fans.' },
          { beat_id: 'beat_2', beat_type: 'CLIMAX', text: 'Decisive brace in European Cup Final.' }
        ],
        climax: 'Scoring the match-winning brace in the 88th minute of the European Cup Final.',
        resolution: 'Firmly cementing his name into modern club football history.',
        themes: ['Persistence', 'Excellence', 'Loyalty']
      },
      script: {
        script_id: 'script_01',
        title: 'Documentary Presentation Script',
        hook: { text: 'He arrived with nothing but raw potential and unwavering determination.' },
        sections: [
          {
            title: 'I. The Early Promise',
            segments: [{ text: 'In 2024, Adrian joined the academy system with high expectations.' }]
          },
          {
            title: 'II. The European Zenith',
            segments: [{ text: 'By 2030, he had grown into the most feared forward in the league.' }]
          }
        ],
        climax: { text: 'With seconds remaining, Martínez fires into the top corner—sealing the Champions League!' },
        closing: { text: 'At just 24 years old, the story of Adrian Martínez is far from over.' },
        word_count: 420,
        estimated_duration_seconds: 165
      },
      metadata: {
        presentation_id: `pres_${playerId}`,
        player_id: playerId,
        density: PresentationDensity.STANDARD,
        generated_at_timestamp: Date.now(),
        presentation_version: '1.0'
      }
    };
  }
}
