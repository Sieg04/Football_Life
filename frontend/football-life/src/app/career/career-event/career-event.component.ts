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

  onContinue(): void {
    this.dismiss.emit();
  }
}
