import { Routes } from '@angular/router';

export const routes: Routes = [{
  path: '',
  loadComponent: () => import('./features/report-builder/report-builder').then(m => m.ReportBuilder),
}, { path: '**', redirectTo: '' }];
