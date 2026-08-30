import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CareerSessionService, CareerSession } from '../../core/services/career-session.service';

@Component({
  selector: 'app-career-shell',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './career-shell.component.html',
  styleUrls: ['./career-shell.component.scss']
})
export class CareerShellComponent implements OnInit {
  session: CareerSession | null = null;
  recordingMode = false;

  navItems = [
    { label: 'DASHBOARD', path: '/dashboard' },
    { label: 'NEW CAREER', path: '/create' },
    { label: 'CAREER', path: '/career' },
    { label: 'PROFILE', path: '/profile' },
    { label: 'TIMELINE', path: '/timeline' },
    { label: 'STATS', path: '/stats' },
    { label: 'CLUBS', path: '/clubs' },
    { label: 'ACHIEVEMENTS', path: '/achievements' },
    { label: 'STORY', path: '/story' },
    { label: 'SCRIPT', path: '/script' }
  ];

  constructor(private sessionService: CareerSessionService) {}

  ngOnInit(): void {
    this.sessionService.activeSession$.subscribe((s) => {
      this.session = s;
    });
    this.sessionService.recordingMode$.subscribe((rec) => {
      this.recordingMode = rec;
    });
  }

  get currentSeason(): string {
    return this.session?.current_season || '2026/27';
  }

  get playerName(): string {
    return this.session?.presentation?.player?.name || 'ADRIAN MARTÍNEZ';
  }

  get playerOvr(): number {
    return this.session?.presentation?.player?.overall_rating || 75;
  }
}
