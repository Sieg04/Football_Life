import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-scene-controls',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './scene-controls.component.html',
  styleUrls: ['./scene-controls.component.scss']
})
export class SceneControlsComponent {
  @Input() currentSceneIndex: number = 0;
  @Input() totalScenes: number = 0;
  @Input() isPlaying: boolean = false;
  @Input() playbackProgress: number = 0;
  @Input() currentDurationSeconds: number = 5;

  @Output() play = new EventEmitter<void>();
  @Output() pause = new EventEmitter<void>();
  @Output() previous = new EventEmitter<void>();
  @Output() next = new EventEmitter<void>();
  @Output() seek = new EventEmitter<number>();
  @Output() toggleCapture = new EventEmitter<void>();

  onTogglePlayPause(): void {
    if (this.isPlaying) {
      this.pause.emit();
    } else {
      this.play.emit();
    }
  }

  onPrev(): void {
    this.previous.emit();
  }

  onNext(): void {
    this.next.emit();
  }

  onSeek(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target) {
      this.seek.emit(parseFloat(target.value));
    }
  }

  onCapture(): void {
    this.toggleCapture.emit();
  }
}
