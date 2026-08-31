import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface TransferOfferUI {
  offer_id: string;
  destination_club_name: string;
  country_code: string;
  league_name: string;
  club_prestige: number;
  transfer_type: string;
  transfer_fee: number;
  weekly_salary: number;
  contract_years: number;
  proposed_role: string;
  expected_playing_time: string;
  career_impact: string;
  interest_reason: string;
}

@Component({
  selector: 'app-career-transfer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './career-transfer.component.html',
  styleUrls: ['./career-transfer.component.scss']
})
export class CareerTransferComponent {
  @Input() offers: TransferOfferUI[] = [];
  @Input() currentClub = 'Real Madrid';
  @Output() selectAction = new EventEmitter<{ offerId: string; action: string }>();

  selectedOfferIndex = 0;

  get selectedOffer(): TransferOfferUI | null {
    return this.offers.length > 0 ? this.offers[this.selectedOfferIndex] : null;
  }

  onAccept(): void {
    if (this.selectedOffer) {
      this.selectAction.emit({ offerId: this.selectedOffer.offer_id, action: 'ACCEPT' });
    }
  }

  onReject(): void {
    if (this.selectedOffer) {
      this.selectAction.emit({ offerId: this.selectedOffer.offer_id, action: 'REJECT' });
    }
  }

  onStay(): void {
    this.selectAction.emit({ offerId: '', action: 'STAY' });
  }

  formatFee(fee: number): string {
    if (fee === 0) return 'FREE / LOAN';
    if (fee >= 1000000) return `€${(fee / 1000000).toFixed(1)}M`;
    return `€${(fee / 1000).toFixed(0)}K`;
  }

  formatSalary(sal: number): string {
    return `€${(sal / 1000).toFixed(0)}K / week`;
  }
}
