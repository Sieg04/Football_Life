import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CareerSessionService, CareerSetupRequest } from '../../core/services/career-session.service';

interface CountryOption {
  code: string;
  name: string;
}

interface LeagueOption {
  code: string;
  name: string;
  country_code: string;
}

interface ClubOption {
  id: string;
  name: string;
  league_code: string;
  prestige: number;
}

@Component({
  selector: 'app-career-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './career-create.component.html',
  styleUrls: ['./career-create.component.scss']
})
export class CareerCreateComponent {
  playerName = 'Adrian Martínez';
  selectedPosition = 'ST';
  nationality = 'Spain';
  selectedCountry = 'ESP';
  selectedLeague = 'ESP1';
  startingClub = 'Real Madrid';
  loading = false;

  positions = ['ST', 'LW', 'RW', 'CAM', 'CM', 'CB', 'GK'];

  nationalities = ['Spain', 'England', 'Germany', 'France', 'Italy', 'Brazil', 'Argentina', 'Portugal'];

  countries: CountryOption[] = [
    { code: 'ESP', name: 'Spain' },
    { code: 'ENG', name: 'England' },
    { code: 'GER', name: 'Germany' },
    { code: 'FRA', name: 'France' },
    { code: 'ITA', name: 'Italy' },
  ];

  leagues: LeagueOption[] = [
    { code: 'ESP1', name: 'La Liga', country_code: 'ESP' },
    { code: 'ESP2', name: 'La Liga Hypermotion', country_code: 'ESP' },
    { code: 'ENG1', name: 'Premier League', country_code: 'ENG' },
    { code: 'ENG2', name: 'EFL Championship', country_code: 'ENG' },
    { code: 'GER1', name: 'Bundesliga', country_code: 'GER' },
    { code: 'FRA1', name: 'Ligue 1', country_code: 'FRA' },
    { code: 'ITA1', name: 'Serie A', country_code: 'ITA' },
  ];

  allClubs: ClubOption[] = [
    { id: 'Real Madrid', name: 'Real Madrid', league_code: 'ESP1', prestige: 92 },
    { id: 'FC Barcelona', name: 'FC Barcelona', league_code: 'ESP1', prestige: 90 },
    { id: 'Atlético Madrid', name: 'Atlético Madrid', league_code: 'ESP1', prestige: 85 },
    { id: 'Real Betis', name: 'Real Betis', league_code: 'ESP1', prestige: 75 },
    { id: 'RCD Espanyol', name: 'RCD Espanyol', league_code: 'ESP2', prestige: 65 },
    { id: 'Manchester City', name: 'Manchester City', league_code: 'ENG1', prestige: 94 },
    { id: 'Arsenal', name: 'Arsenal', league_code: 'ENG1', prestige: 88 },
    { id: 'Liverpool', name: 'Liverpool', league_code: 'ENG1', prestige: 89 },
    { id: 'Leeds United', name: 'Leeds United', league_code: 'ENG2', prestige: 70 },
    { id: 'Bayern Munich', name: 'Bayern Munich', league_code: 'GER1', prestige: 92 },
    { id: 'PSG', name: 'PSG', league_code: 'FRA1', prestige: 89 },
    { id: 'Inter Milan', name: 'Inter Milan', league_code: 'ITA1', prestige: 87 },
  ];

  filteredLeagues: LeagueOption[] = [];
  filteredClubs: ClubOption[] = [];
  selectedClubInfo: ClubOption | null = null;

  constructor(
    private sessionService: CareerSessionService,
    private router: Router
  ) {
    this.onCountryChange();
  }

  onCountryChange(): void {
    this.filteredLeagues = this.leagues.filter(l => l.country_code === this.selectedCountry);
    if (this.filteredLeagues.length > 0) {
      this.selectedLeague = this.filteredLeagues[0].code;
      this.onLeagueChange();
    } else {
      this.filteredClubs = [];
      this.startingClub = '';
      this.selectedClubInfo = null;
    }
  }

  onLeagueChange(): void {
    this.filteredClubs = this.allClubs.filter(c => c.league_code === this.selectedLeague);
    if (this.filteredClubs.length > 0) {
      this.startingClub = this.filteredClubs[0].id;
      this.onClubChange();
    } else {
      this.startingClub = '';
      this.selectedClubInfo = null;
    }
  }

  onClubChange(): void {
    this.selectedClubInfo = this.allClubs.find(c => c.id === this.startingClub) || null;
  }

  onStartCareer(): void {
    if (!this.playerName.trim() || !this.startingClub) return;
    this.loading = true;

    const request: CareerSetupRequest = {
      player_name: this.playerName,
      position: this.selectedPosition,
      starting_club_id: this.startingClub,
      nationality: this.nationality
    };

    this.sessionService.createCareer(request).subscribe(() => {
      this.loading = false;
      this.router.navigate(['/career/dashboard']);
    });
  }
}
