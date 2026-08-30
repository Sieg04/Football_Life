import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CaptureFrame } from '../../core/models/replay.model';

@Component({
  selector: 'app-capture-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './capture-view.component.html',
  styleUrls: ['./capture-view.component.scss']
})
export class CaptureViewComponent {
  @Input() captureFrame: CaptureFrame | null = null;
  @Input() presets: string[] = ['STANDARD_1080P', 'BROADCAST_OVERLAY', 'SOCIAL_CARD', 'MINIMAL_BANNER'];
  @Input() selectedPreset: string = 'STANDARD_1080P';

  @Output() presetChange = new EventEmitter<string>();
  @Output() closeView = new EventEmitter<void>();

  onSelectPreset(preset: string): void {
    this.presetChange.emit(preset);
  }

  onClose(): void {
    this.closeView.emit();
  }
}
