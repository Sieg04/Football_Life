import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Decision, DecisionOption } from '../../core/services/career-session.service';

@Component({
  selector: 'app-career-decision',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-decision.component.html',
  styleUrls: ['./career-decision.component.scss']
})
export class CareerDecisionComponent {
  @Input() decision: Decision | null = null;
  @Output() selectOption = new EventEmitter<string>();

  onChoice(option: DecisionOption): void {
    this.selectOption.emit(option.id);
  }
}
