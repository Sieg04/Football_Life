import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-career-achievements',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-achievements.component.html',
  styleUrls: ['./career-achievements.component.scss']
})
export class CareerAchievementsComponent implements OnInit {
  presentation: CareerPresentation | null = null;

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
    });
  }
}
