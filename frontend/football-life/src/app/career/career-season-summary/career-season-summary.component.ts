import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-career-season-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-season-summary.component.html',
  styleUrls: ['./career-season-summary.component.scss']
})
export class CareerSeasonSummaryComponent {
  @Input() summary: any = null;
  @Output() close = new EventEmitter<void>();

  onClose(): void {
    this.close.emit();
  }
}
