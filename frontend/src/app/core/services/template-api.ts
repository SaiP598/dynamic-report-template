import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TemplateResponse } from '../models/template';

@Injectable({ providedIn: 'root' })
export class TemplateApi {
  private readonly http = inject(HttpClient);

  loadCurrent() {
    return this.http.get<TemplateResponse>('/api/templates/current');
  }
}
