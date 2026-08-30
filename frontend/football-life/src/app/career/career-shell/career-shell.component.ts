import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation } from '../../core/models/presentation.model';

@Component({
  selector: 'app-career-shell',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './career-shell.component.html',
  styleUrls: ['./career-shell.component.scss']
})
export class CareerShellComponent implements OnInit {
  presentation: CareerPresentation | null = null;
  loading = true;

  navItems = [
    { label: 'CAREER', path: '/career' },
    { label: 'PROFILE', path: '/profile' },
    { label: 'TIMELINE', path: '/timeline' },
    { label: 'STATS', path: '/stats' },
    { label: 'CLUBS', path: '/clubs' },
    { label: 'ACHIEVEMENTS', path: '/achievements' },
    { label: 'STORY', path: '/story' },
    { label: 'SCRIPT', path: '/script' }
  ];

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
      this.loading = false;
    });
  }
}
