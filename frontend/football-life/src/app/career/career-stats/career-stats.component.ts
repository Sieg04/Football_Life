import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';
import { StatCardComponent } from '../stat-card/stat-card.component';

@Component({
  selector: 'app-career-stats',
  standalone: true,
  imports: [CommonModule, StatCardComponent],
  templateUrl: './career-stats.component.html',
  styleUrls: ['./career-stats.component.scss']
})
export class CareerStatsComponent implements OnInit {
  presentation: CareerPresentation | null = null;

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
    });
  }
}
