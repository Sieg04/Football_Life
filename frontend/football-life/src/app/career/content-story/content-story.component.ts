import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ReplayService } from '../../core/services/replay.service';
import { CareerSessionService } from '../../core/services/career-session.service';
import { CareerReplay, ContentStory, ReplayMoment, ContentScene, CaptureFrame } from '../../core/models/replay.model';
import { CareerMomentsComponent } from '../career-moments/career-moments.component';
import { ContentSceneComponent } from '../content-scene/content-scene.component';
import { SceneControlsComponent } from '../scene-controls/scene-controls.component';
import { CaptureViewComponent } from '../capture-view/capture-view.component';

@Component({
  selector: 'app-content-story',
  standalone: true,
  imports: [
    CommonModule,
    CareerMomentsComponent,
    ContentSceneComponent,
    SceneControlsComponent,
    CaptureViewComponent
  ],
  templateUrl: './content-story.component.html',
  styleUrls: ['./content-story.component.scss']
})
export class ContentStoryComponent implements OnInit, OnDestroy {
  careerId: string = 'test-session';
  careerReplay: CareerReplay | null = null;
  contentStory: ContentStory | null = null;
  selectedMomentIds: string[] = [];

  activeTab: 'MOMENTS' | 'STORY' | 'CAPTURE' = 'MOMENTS';
  currentSceneIndex: number = 0;
  isPlaying: boolean = false;
  playbackProgress: number = 0;
  playbackTimer: any = null;

  showCaptureModal: boolean = false;
  currentCaptureFrame: CaptureFrame | null = null;
  selectedPreset: string = 'STANDARD_1080P';

  isLoading: boolean = false;
  errorMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private replayService: ReplayService,
    private sessionService: CareerSessionService
  ) {}

  ngOnInit(): void {
    const session = this.sessionService.currentSession;
    if (session && session.career_id) {
      this.careerId = session.career_id;
    }

    this.loadReplayData();
  }

  ngOnDestroy(): void {
    this.stopPlayback();
  }

  loadReplayData(): void {
    this.isLoading = true;
    this.replayService.getCareerReplay(this.careerId).subscribe({
      next: (replay: CareerReplay) => {
        this.careerReplay = replay;
        // Default select top moments
        this.selectedMomentIds = replay.moments.slice(0, 10).map((m: ReplayMoment) => m.moment_id);
        this.buildStory();
      },
      error: (err: any) => {
        this.errorMessage = 'Failed to load career replay data.';
        this.isLoading = false;
      }
    });
  }

  toggleMomentSelection(momentId: string): void {
    const idx = this.selectedMomentIds.indexOf(momentId);
    if (idx >= 0) {
      this.selectedMomentIds.splice(idx, 1);
    } else {
      this.selectedMomentIds.push(momentId);
    }
  }

  selectAllVisibleMoments(): void {
    if (!this.careerReplay) return;
    this.selectedMomentIds = this.careerReplay.moments.map((m: ReplayMoment) => m.moment_id);
  }

  buildStory(): void {
    this.isLoading = true;
    this.replayService.buildContentStory(this.careerId, this.selectedMomentIds).subscribe({
      next: (story: ContentStory) => {
        this.contentStory = story;
        this.currentSceneIndex = 0;
        this.isLoading = false;
      },
      error: (err: any) => {
        this.errorMessage = 'Failed to build content story.';
        this.isLoading = false;
      }
    });
  }

  selectTab(tab: 'MOMENTS' | 'STORY' | 'CAPTURE'): void {
    this.activeTab = tab;
  }

  selectScene(index: number): void {
    this.currentSceneIndex = index;
    this.playbackProgress = 0;
  }

  play(): void {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.startPlaybackTimer();
  }

  pause(): void {
    this.isPlaying = false;
    this.stopPlayback();
  }

  startPlaybackTimer(): void {
    this.stopPlayback();
    this.playbackTimer = setInterval(() => {
      this.playbackProgress += 5;
      if (this.playbackProgress >= 100) {
        this.playbackProgress = 0;
        if (this.contentStory && this.currentSceneIndex < this.contentStory.scenes.length - 1) {
          this.currentSceneIndex++;
        } else {
          this.pause();
        }
      }
    }, 250);
  }

  stopPlayback(): void {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
  }

  previousScene(): void {
    if (this.currentSceneIndex > 0) {
      this.currentSceneIndex--;
      this.playbackProgress = 0;
    }
  }

  nextScene(): void {
    if (this.contentStory && this.currentSceneIndex < this.contentStory.scenes.length - 1) {
      this.currentSceneIndex++;
      this.playbackProgress = 0;
    }
  }

  seek(progress: number): void {
    this.playbackProgress = progress;
  }

  openCaptureView(): void {
    if (!this.contentStory || !this.contentStory.scenes[this.currentSceneIndex]) return;
    const sceneId = this.contentStory.scenes[this.currentSceneIndex].scene_id;
    this.fetchCaptureFrame(sceneId, this.selectedPreset);
  }

  onPresetChange(preset: string): void {
    this.selectedPreset = preset;
    if (this.contentStory && this.contentStory.scenes[this.currentSceneIndex]) {
      const sceneId = this.contentStory.scenes[this.currentSceneIndex].scene_id;
      this.fetchCaptureFrame(sceneId, preset);
    }
  }

  fetchCaptureFrame(sceneId: string, preset: string): void {
    this.replayService.getCaptureFrame(this.careerId, sceneId, preset).subscribe({
      next: (frame: CaptureFrame) => {
        this.currentCaptureFrame = frame;
        this.showCaptureModal = true;
      },
      error: () => {
        this.errorMessage = 'Failed to capture frame.';
      }
    });
  }

  closeCaptureModal(): void {
    this.showCaptureModal = false;
  }

  get currentScene(): ContentScene | null {
    if (!this.contentStory || !this.contentStory.scenes) return null;
    return this.contentStory.scenes[this.currentSceneIndex] || null;
  }
}
