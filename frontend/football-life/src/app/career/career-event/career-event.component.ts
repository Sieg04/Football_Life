import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-career-event',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-event.component.html',
  styleUrls: ['./career-event.component.scss']
})
export class CareerEventComponent {
  @Input() event: any | null = null;
  @Output() dismiss = new EventEmitter<void>();

  get priority(): string {
    const p = (this.event?.priority || this.event?.impact || 'MEDIUM').toString().toUpperCase();
    if (['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].includes(p)) return p;
    return 'HIGH';
  }

  get category(): string {
    return (this.event?.category || this.event?.event_type || 'CAREER MOMENT').toString().toUpperCase();
  }

  onContinue(): void {
    this.dismiss.emit();
  }
}
