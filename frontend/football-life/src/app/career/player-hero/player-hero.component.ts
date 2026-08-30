import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlayerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-player-hero',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './player-hero.component.html',
  styleUrls: ['./player-hero.component.scss']
})
export class PlayerHeroComponent {
  @Input() player!: PlayerPresentation;
}
