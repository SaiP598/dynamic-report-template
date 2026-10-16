import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { TemplateApi } from '../../core/services/template-api';
import { SectionId, TemplateConfiguration } from '../../core/models/template';

const DESCRIPTIONS: Record<SectionId, string> = {
  'current-medications': 'Current medications, unrecognized medications, and items outside scope.',
  'risk-management': 'Risk findings and their supporting details.',
  'impacted-medications': 'Medication categories and color-coded precaution tables.',
  'dosing-guidance': 'Medication findings and guidance, grouped with their evidence.',
  'legend': 'Risk categories, colors, and evidence strength definitions.',
  'test-details': 'Gene, genotype, and phenotype results.',
  'patient-card': 'A compact patient summary to share with other providers.',
};

@Component({
  selector: 'app-report-builder',
  imports: [DragDropModule],
  templateUrl: './report-builder.html',
})
export class ReportBuilder {
  private readonly api = inject(TemplateApi);
  private readonly destroyRef = inject(DestroyRef);
  readonly configuration = signal<TemplateConfiguration | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');
  readonly announcement = signal('');
  readonly edited = signal(false);
  readonly revision = signal(0);
  readonly descriptions = DESCRIPTIONS;

  constructor() { this.load(); }

  load() {
    this.loading.set(true);
    this.error.set('');
    this.api.loadCurrent().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        if (!response.configuration?.sections?.length) {
          this.error.set('No report sections were returned. Please retry loading the template.');
          this.configuration.set(null);
        } else {
          this.configuration.set(response.configuration);
          this.revision.set(response.revision);
          this.edited.set(false);
        }
        this.loading.set(false);
      },
      error: () => {
        this.error.set('We could not load your template. Check that the API and database are running, then retry.');
        this.loading.set(false);
      },
    });
  }

  drop(event: CdkDragDrop<unknown>) {
    this.move(event.previousIndex, event.currentIndex);
  }

  move(from: number, to: number) {
    const current = this.configuration();
    if (!current || from === to || to < 0 || to >= current.sections.length) return;
    const sections = [...current.sections];
    moveItemInArray(sections, from, to);
    this.configuration.set({ ...current, sections });
    this.edited.set(true);
    this.announcement.set(`${sections[to].heading} moved to position ${to + 1} of ${sections.length}.`);
  }

  rename(id: SectionId, event: Event) {
    const heading = (event.target as HTMLInputElement).value;
    this.configuration.update(current => current && ({
      ...current,
      sections: current.sections.map(section => section.id === id ? { ...section, heading } : section),
    }));
    this.edited.set(true);
  }
}
