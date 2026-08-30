import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
    });
  }
}
