import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';
import { PlayerHeroComponent } from '../player-hero/player-hero.component';

@Component({
  selector: 'app-career-hub',
  standalone: true,
  imports: [CommonModule, PlayerHeroComponent],
  templateUrl: './career-hub.component.html',
  styleUrls: ['./career-hub.component.scss']
})
export class CareerHubComponent implements OnInit {
  presentation: CareerPresentation | null = null;
  loading = true;

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
      this.loading = false;
    });
  }
}
