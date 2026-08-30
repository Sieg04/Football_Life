import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-career-story',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-story.component.html',
  styleUrls: ['./career-story.component.scss']
})
export class CareerStoryComponent implements OnInit {
  presentation: CareerPresentation | null = null;

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
    });
  }
}
