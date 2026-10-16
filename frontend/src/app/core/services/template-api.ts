import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TemplateConfiguration, TemplateResponse } from '../models/template';

@Injectable({ providedIn: 'root' })
export class TemplateApi {
  private readonly http = inject(HttpClient);

  save(configuration: TemplateConfiguration) {
    return this.http.put<TemplateResponse>('/api/templates/current', configuration);
  }

  generateReport() {
    return this.http.post('/api/reports', null, { responseType: 'blob', observe: 'response' });
  }

  restore() {
    return this.http.post<TemplateResponse>('/api/templates/current/restore', null);
  }

  loadCurrent() {
    return this.http.get<TemplateResponse>('/api/templates/current');
  }
}
