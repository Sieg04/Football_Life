import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CareerSessionNotification } from '../../core/services/career-session.service';

@Component({
  selector: 'app-career-notification',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-notification.component.html',
  styleUrls: ['./career-notification.component.scss']
})
export class CareerNotificationComponent {
  @Input() notifications: CareerSessionNotification[] = [];
}
