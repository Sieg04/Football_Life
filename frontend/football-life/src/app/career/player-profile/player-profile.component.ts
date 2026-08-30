import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerSessionService, CareerSession } from '../../core/services/career-session.service';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-player-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './player-profile.component.html',
  styleUrls: ['./player-profile.component.scss']
})
export class PlayerProfileComponent implements OnInit {
  presentation: CareerPresentation | null = null;
  session: CareerSession | null = null;

  constructor(
    private sessionService: CareerSessionService,
    private presentationService: CareerPresentationService
  ) {}

  ngOnInit(): void {
    this.sessionService.activeSession$.subscribe((s) => {
      this.session = s;
      if (s?.presentation) {
        this.presentation = s.presentation;
      }
    });

    if (!this.presentation) {
      this.presentationService.getPresentation().subscribe((data) => {
        this.presentation = data;
      });
    }
  }
}
