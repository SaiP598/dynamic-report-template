import { Component, inject, signal } from '@angular/core';
import { HealthApi } from '../../core/services/health-api';

@Component({
  selector: 'app-report-builder',
  templateUrl: './report-builder.html',
})
export class ReportBuilder {
  readonly apiStatus = signal('Checking API connection…');
  constructor() {
    inject(HealthApi).check().subscribe({
      next: () => this.apiStatus.set('API connected'),
      error: () => this.apiStatus.set('API unavailable — start Flask on port 5000.'),
    });
  }
}
