import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReplayMoment } from '../../core/models/replay.model';

@Component({
  selector: 'app-career-moments',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-moments.component.html',
  styleUrls: ['./career-moments.component.scss']
})
export class CareerMomentsComponent implements OnInit, OnChanges {
  @Input() moments: ReplayMoment[] = [];
  @Input() selectedMomentIds: string[] = [];
  @Output() toggleMoment = new EventEmitter<string>();
  @Output() selectAllMoments = new EventEmitter<void>();

  filteredMoments: ReplayMoment[] = [];
  activePriorityFilter: string = 'ALL';
  activeTypeFilter: string = 'ALL';

  priorities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  types = ['ALL', 'CAREER_START', 'DEBUT', 'GOAL_MILESTONE', 'TRANSFER', 'ACHIEVEMENT', 'TURNING_POINT', 'CONFLICT'];

  ngOnInit(): void {
    this.applyFilters();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['moments']) {
      this.applyFilters();
    }
  }

  setPriorityFilter(prio: string): void {
    this.activePriorityFilter = prio;
    this.applyFilters();
  }

  setTypeFilter(type: string): void {
    this.activeTypeFilter = type;
    this.applyFilters();
  }

  applyFilters(): void {
    let result = [...this.moments];
    if (this.activePriorityFilter !== 'ALL') {
      result = result.filter((m) => m.priority === this.activePriorityFilter);
    }
    if (this.activeTypeFilter !== 'ALL') {
      result = result.filter((m) => m.moment_type === this.activeTypeFilter);
    }
    this.filteredMoments = result;
  }

  isSelected(momentId: string): boolean {
    return this.selectedMomentIds.includes(momentId);
  }

  onToggle(momentId: string): void {
    this.toggleMoment.emit(momentId);
  }

  onSelectAll(): void {
    this.selectAllMoments.emit();
  }
}
