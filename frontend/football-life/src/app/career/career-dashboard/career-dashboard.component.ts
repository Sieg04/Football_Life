import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import {
  CareerSessionService,
  CareerSession,
  CareerSessionStatus
} from '../../core/services/career-session.service';
import { CareerEventComponent } from '../career-event/career-event.component';
import { CareerDecisionComponent } from '../career-decision/career-decision.component';
import { CareerNotificationComponent } from '../career-notification/career-notification.component';
import { CareerRecordingModeComponent } from '../career-recording-mode/career-recording-mode.component';

@Component({
  selector: 'app-career-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    CareerEventComponent,
    CareerDecisionComponent,
    CareerNotificationComponent,
    CareerRecordingModeComponent
  ],
  templateUrl: './career-dashboard.component.html',
  styleUrls: ['./career-dashboard.component.scss']
})
export class CareerDashboardComponent implements OnInit {
  session: CareerSession | null = null;
  recordingMode = false;
  advancing = false;
  activeOverlayEvent: any | null = null;

  constructor(
    public sessionService: CareerSessionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.sessionService.activeSession$.subscribe((s) => {
      this.session = s;
      if (s && s.pending_events && s.pending_events.length > 0 && !this.activeOverlayEvent) {
        this.activeOverlayEvent = s.pending_events[s.pending_events.length - 1];
      }
    });

    this.sessionService.recordingMode$.subscribe((rec) => {
      this.recordingMode = rec;
    });

    // If no session is active, load default or fallback session
    if (!this.session) {
      this.sessionService.getCareerSession('sample').subscribe();
    }
  }

  onAdvance(): void {
    if (!this.session || this.advancing) return;
    if (this.session.status === CareerSessionStatus.DECISION_PENDING) return;

    this.advancing = true;
    this.sessionService.advanceCareer(this.session.career_id).subscribe({
      next: (result) => {
        this.advancing = false;
        if (result.processed_events && result.processed_events.length > 0) {
          this.activeOverlayEvent = result.processed_events[result.processed_events.length - 1];
        }
      },
      error: () => {
        this.advancing = false;
      }
    });
  }

  onResolveDecision(optionId: string): void {
    if (!this.session || !this.session.pending_decision) return;
    this.sessionService
      .resolveDecision(this.session.career_id, this.session.pending_decision.id, optionId)
      .subscribe();
  }

  onDismissEvent(): void {
    this.activeOverlayEvent = null;
  }

  onToggleRecordingMode(): void {
    this.sessionService.toggleRecordingMode();
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}
