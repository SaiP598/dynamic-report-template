import { Component, computed, DestroyRef, HostListener, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { TemplateApi } from '../../core/services/template-api';
import { SectionId, TemplateConfiguration, TemplateResponse, TextFormatting } from '../../core/models/template';

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
  imports: [DragDropModule, FormsModule],
  templateUrl: './report-builder.html',
})
export class ReportBuilder {
  private readonly api = inject(TemplateApi);
  private readonly destroyRef = inject(DestroyRef);
  readonly configuration = signal<TemplateConfiguration | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');
  readonly announcement = signal('');
  private readonly saved = signal('');
  readonly edited = computed(() => JSON.stringify(this.configuration()) !== this.saved());
  readonly busy = signal(false);
  readonly feedback = signal('');
  readonly generating = signal(false);
  readonly downloadError = signal('');
  readonly downloadStatus = signal('');
  readonly actionError = signal('');
  readonly confirmingRestore = signal(false);
  readonly formattingTargets = ['header', 'footer'] as const;
  readonly valid = computed(() => {
    const current = this.configuration();
    return !!current && current.sections.every(s => !!s.heading.trim() && s.heading.length <= 120)
      && this.formattingTargets.every(key => {
        const f = current[key];
        return f.text.length <= 1000 && Number.isInteger(f.fontSize) && f.fontSize >= 6 && f.fontSize <= 36;
      });
  });
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
          this.acceptSaved(response);
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
    if (this.busy() || !current || from === to || to < 0 || to >= current.sections.length) return;
    const sections = [...current.sections];
    moveItemInArray(sections, from, to);
    this.configuration.set({ ...current, sections });
    this.clearFeedback();
    this.announcement.set(`${sections[to].heading} moved to position ${to + 1} of ${sections.length}.`);
  }

  rename(id: SectionId, event: Event) {
    if (this.busy()) return;
    const heading = (event.target as HTMLInputElement).value;
    this.configuration.update(current => current && ({
      ...current,
      sections: current.sections.map(section => section.id === id ? { ...section, heading } : section),
    }));
    this.clearFeedback();
  }

  updateFormatting(target: 'header' | 'footer', patch: Partial<TextFormatting>) {
    if (this.busy()) return;
    this.configuration.update(current => current && ({ ...current, [target]: { ...current[target], ...patch } }));
    this.clearFeedback();
  }

  private clearFeedback() {
    this.feedback.set('');
    this.actionError.set('');
  }

  private acceptSaved(response: TemplateResponse) {
    this.configuration.set(response.configuration);
    this.saved.set(JSON.stringify(response.configuration));
    this.revision.set(response.revision);
  }

  save() {
    const current = this.configuration();
    if (this.busy() || !current || !this.valid() || !this.edited()) return;
    this.busy.set(true);
    this.clearFeedback();
    this.api.save(current).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.acceptSaved(response);
        this.busy.set(false);
        this.feedback.set('Template saved. Your changes will be available when you reopen the editor.');
      },
      error: () => {
        this.busy.set(false);
        this.actionError.set('Could not save the template. Your edits are still here. Please try saving again.');
      },
    });
  }

  restore() {
    if (this.busy() || !this.confirmingRestore()) return;
    this.busy.set(true);
    this.clearFeedback();
    this.api.restore().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.acceptSaved(response);
        this.busy.set(false);
        this.confirmingRestore.set(false);
        this.feedback.set('Default template restored and saved.');
      },
      error: () => {
        this.busy.set(false);
        this.actionError.set('Could not restore the default. Your current edits are unchanged. Please try again.');
      },
    });
  }

  downloadReport() {
    if (this.generating() || this.busy()) return;
    this.generating.set(true);
    this.downloadError.set('');
    this.downloadStatus.set('');
    this.api.generateReport().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.generating.set(false);
        if (!response.body) {
          this.downloadError.set('The report was empty. Please try again.');
          return;
        }
        const url = URL.createObjectURL(response.body);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'dynamic-report.pdf';
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        this.downloadStatus.set('Report downloaded from saved revision ' + (response.headers.get('X-Template-Revision') ?? this.revision()) + '.');
      },
      error: () => {
        this.generating.set(false);
        this.downloadError.set('Could not generate the report. Your edits are unchanged. Please try again.');
      },
    });
  }

  @HostListener('window:beforeunload', ['$event'])
  warnBeforeLeaving(event: BeforeUnloadEvent) {
    if (this.edited() && this.configuration()) {
      event.preventDefault();
      event.returnValue = '';
    }
  }

}
