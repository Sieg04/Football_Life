import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContentScene } from '../../core/models/replay.model';

@Component({
  selector: 'app-content-scene',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './content-scene.component.html',
  styleUrls: ['./content-scene.component.scss']
})
export class ContentSceneComponent {
  @Input() scene!: ContentScene;
  @Input() isActive: boolean = false;
  @Input() index: number = 0;
  @Output() sceneSelected = new EventEmitter<number>();

  onSelect(): void {
    this.sceneSelected.emit(this.index);
  }
}
