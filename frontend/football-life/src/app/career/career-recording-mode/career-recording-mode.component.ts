import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-career-recording-mode',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-recording-mode.component.html',
  styleUrls: ['./career-recording-mode.component.scss']
})
export class CareerRecordingModeComponent {
  @Input() active = false;
  @Output() toggle = new EventEmitter<void>();

  onToggle(): void {
    this.toggle.emit();
  }
}
