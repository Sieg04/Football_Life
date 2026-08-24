import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { catchError, of } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [AsyncPipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  private readonly http = inject(HttpClient);

  readonly health$ = this.http.get<{ status: string }>('http://localhost:8000/health').pipe(
    catchError(() => of({ status: 'offline' }))
  );
}
