import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TimelineEntry, VisualPriority } from '../../core/models/presentation.model';

@Component({
  selector: 'app-timeline-entry',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './timeline-entry.component.html',
  styleUrls: ['./timeline-entry.component.scss']
})
export class TimelineEntryComponent {
  @Input() entry!: TimelineEntry;

  get priorityClass(): string {
    switch (this.entry?.priority) {
      case VisualPriority.CRITICAL:
        return 'prio-critical';
      case VisualPriority.HIGH:
        return 'prio-high';
      default:
        return 'prio-standard';
    }
  }
}
