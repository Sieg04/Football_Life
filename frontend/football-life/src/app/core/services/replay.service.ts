import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { CareerReplay, ContentStory, ReplayMoment, CaptureFrame } from '../models/replay.model';

@Injectable({
  providedIn: 'root'
})
export class ReplayService {
  private apiUrl = 'http://localhost:8000/career';

  constructor(private http: HttpClient) {}

  getCareerReplay(careerId: string): Observable<CareerReplay> {
    return this.http.get<CareerReplay>(`${this.apiUrl}/${careerId}/replay`);
  }

  getReplayMoments(careerId: string, priority?: string, momentType?: string): Observable<ReplayMoment[]> {
    let url = `${this.apiUrl}/${careerId}/replay/moments`;
    const params: string[] = [];
    if (priority) params.push(`priority=${priority}`);
    if (momentType) params.push(`moment_type=${momentType}`);
    if (params.length > 0) {
      url += `?${params.join('&')}`;
    }
    return this.http.get<any>(url).pipe(
      map((res) => (res && res.moments ? res.moments : res))
    );
  }

  buildContentStory(careerId: string, selectedMomentIds?: string[]): Observable<ContentStory> {
    return this.http.post<ContentStory>(`${this.apiUrl}/${careerId}/content-story`, {
      selected_moment_ids: selectedMomentIds || [],
      moment_ids: selectedMomentIds || []
    });
  }

  getContentStory(careerId: string): Observable<ContentStory> {
    return this.http.get<ContentStory>(`${this.apiUrl}/${careerId}/content-story`);
  }

  reorderStoryScenes(careerId: string, sceneOrder: string[]): Observable<ContentStory> {
    return this.http.put<ContentStory>(`${this.apiUrl}/${careerId}/content-story/order`, {
      scene_order: sceneOrder,
      scene_ids: sceneOrder
    });
  }

  getCaptureFrame(careerId: string, sceneId: string, preset: string = 'STANDARD_1080P'): Observable<CaptureFrame> {
    return this.http.get<CaptureFrame>(`${this.apiUrl}/${careerId}/capture/${sceneId}?preset=${preset}`);
  }
}
