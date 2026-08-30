import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerPresentationService } from '../../core/services/presentation.service';
import { CareerPresentation, TimelineEntry, VisualPriority } from '../../core/models/presentation.model';
import { TimelineEntryComponent } from '../timeline-entry/timeline-entry.component';

@Component({
  selector: 'app-career-timeline',
  standalone: true,
  imports: [CommonModule, TimelineEntryComponent],
  templateUrl: './career-timeline.component.html',
  styleUrls: ['./career-timeline.component.scss']
})
export class CareerTimelineComponent implements OnInit {
  presentation: CareerPresentation | null = null;
  filteredEntries: TimelineEntry[] = [];
  selectedPriority: string = 'ALL';

  constructor(private presentationService: CareerPresentationService) {}

  ngOnInit(): void {
    this.presentationService.getPresentation().subscribe((data) => {
      this.presentation = data;
      this.applyFilter('ALL');
    });
  }

  applyFilter(priority: string): void {
    this.selectedPriority = priority;
    if (!this.presentation) return;

    if (priority === 'ALL') {
      this.filteredEntries = [...this.presentation.timeline];
    } else {
      this.filteredEntries = this.presentation.timeline.filter(
        (e) => e.priority === priority
      );
    }
  }
}
