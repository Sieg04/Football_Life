import { Routes } from '@angular/router';
import { CareerShellComponent } from './career/career-shell/career-shell.component';
import { CareerHubComponent } from './career/career-hub/career-hub.component';
import { PlayerProfileComponent } from './career/player-profile/player-profile.component';
import { CareerTimelineComponent } from './career/career-timeline/career-timeline.component';
import { CareerStatsComponent } from './career/career-stats/career-stats.component';
import { CareerClubsComponent } from './career/career-clubs/career-clubs.component';
import { CareerAchievementsComponent } from './career/career-achievements/career-achievements.component';
import { CareerStoryComponent } from './career/career-story/career-story.component';
import { CareerScriptComponent } from './career/career-script/career-script.component';

export const routes: Routes = [
  {
    path: '',
    component: CareerShellComponent,
    children: [
      { path: '', redirectTo: 'career', pathMatch: 'full' },
      { path: 'career', component: CareerHubComponent },
      { path: 'profile', component: PlayerProfileComponent },
      { path: 'timeline', component: CareerTimelineComponent },
      { path: 'stats', component: CareerStatsComponent },
      { path: 'clubs', component: CareerClubsComponent },
      { path: 'achievements', component: CareerAchievementsComponent },
      { path: 'story', component: CareerStoryComponent },
      { path: 'script', component: CareerScriptComponent }
    ]
  },
  { path: '**', redirectTo: '' }
];
