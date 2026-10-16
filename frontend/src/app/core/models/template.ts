// Version-one configuration and API response contracts.
export type SectionId = 'current-medications' | 'risk-management' | 'impacted-medications'
  | 'dosing-guidance' | 'legend' | 'test-details' | 'patient-card';
export interface TextFormatting {
  text: string;
  alignment: 'left' | 'center' | 'right';
  fontSize: number;
  bold: boolean;
  italic: boolean;
  color: string;
}
export interface TemplateConfiguration {
  schemaVersion: 1;
  sections: { id: SectionId; heading: string }[];
  header: TextFormatting;
  footer: TextFormatting;
}

export interface TemplateResponse {
  configuration: TemplateConfiguration;
  revision: number;
  updatedAt: string | null;
  isDefault: boolean;
}
