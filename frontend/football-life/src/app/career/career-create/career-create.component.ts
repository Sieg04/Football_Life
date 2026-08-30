import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CareerSessionService, CareerSetupRequest } from '../../core/services/career-session.service';

@Component({
  selector: 'app-career-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './career-create.component.html',
  styleUrls: ['./career-create.component.scss']
})
export class CareerCreateComponent {
  playerName = 'Adrian Martínez';
  selectedPosition = 'ST';
  startingClub = 'FC Barcelona';
  nationality = 'Spain';
  loading = false;

  positions = ['ST', 'LW', 'RW', 'CAM', 'CM', 'CB', 'GK'];

  constructor(
    private sessionService: CareerSessionService,
    private router: Router
  ) {}

  onStartCareer(): void {
    if (!this.playerName.trim()) return;
    this.loading = true;

    const request: CareerSetupRequest = {
      player_name: this.playerName,
      position: this.selectedPosition,
      starting_club_id: this.startingClub,
      nationality: this.nationality
    };

    this.sessionService.createCareer(request).subscribe(() => {
      this.loading = false;
      this.router.navigate(['/career/dashboard']);
    });
  }
}
