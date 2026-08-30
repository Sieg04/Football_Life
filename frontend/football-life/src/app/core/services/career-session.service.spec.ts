import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CareerSessionService, CareerSessionStatus } from './career-session.service';

describe('CareerSessionService', () => {
  let service: CareerSessionService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CareerSessionService]
    });
    service = TestBed.inject(CareerSessionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should toggle recording mode', (done) => {
    service.recordingMode$.subscribe((active) => {
      if (active) {
        expect(active).toBeTrue();
        done();
      }
    });
    service.toggleRecordingMode();
  });

  it('should create career and emit active session', (done) => {
    service.createCareer({ player_name: 'Test Striker', position: 'ST' }).subscribe((session) => {
      expect(session).toBeTruthy();
      expect(session.presentation.player.name).toBe('Test Striker');
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/career');
    expect(req.request.method).toBe('POST');
    req.flush({
      career_id: 'cs_test_1',
      player_id: 'p_test_1',
      current_season: '2026/27',
      simulation_position: 1,
      status: CareerSessionStatus.ACTIVE,
      career: {},
      career_record: {},
      presentation: {
        presentation_id: 'pres_1',
        player: { name: 'Test Striker', overall_rating: 80, position: 'ST' },
        overview: { matches: 10, goals: 5 },
        statistics: {},
        clubs: [],
        seasons: [],
        timeline: [],
        highlights: [],
        career_arcs: [],
        relationships: [],
        metadata: {}
      },
      seed: 'SEED-123'
    });
  });
});
