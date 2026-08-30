import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-career-clubs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-clubs.component.html',
  styleUrls: ['./career-clubs.component.scss']
})
export class CareerClubsComponent implements OnInit {
  presentation: CareerPresentation | null = null;

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
    });
  }
}
