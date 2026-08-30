import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { CareerPresentationService } from './presentation.service';

describe('CareerPresentationService', () => {
  let service: CareerPresentationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CareerPresentationService, provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(CareerPresentationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return fallback presentation', () => {
    const fallback = service.getFallbackPresentation('player_1');
    expect(fallback).toBeTruthy();
    expect(fallback.player.player_id).toBe('player_1');
  });
});
