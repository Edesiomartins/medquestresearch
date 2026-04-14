export interface OutcomeExtraction {
  outcome_id: string;
  outcome_name: string;
  outcome_type: 'continuous' | 'binary' | 'generic';
  measure_type?: string;
  intervention_mean?: number;
  intervention_sd?: number;
  intervention_events?: number;
  intervention_total?: number;
  comparator_mean?: number;
  comparator_sd?: number;
  comparator_events?: number;
  comparator_total?: number;
  evidence_snippets: string[];
  page_hints: string[];
  needs_user_confirmation: boolean;
}

export interface StudyExtraction {
  study_id: string;
  citation: string;
  year?: number;
  country?: string;
  design?: string;
  sample_size?: number;
  outcomes: OutcomeExtraction[];
  included: boolean;
  exclusion_reason?: string;
}

export interface PooledResult {
  effect: number;
  ci_low: number;
  ci_high: number;
  se: number;
  z_value: number;
  p_value: number;
  model: string;
  effect_measure: string;
  k: number;
}

export interface HeterogeneityResult {
  Q: number;
  df: number;
  I2: number;
  tau2: number;
  p_heterogeneity: number;
}

export interface PublicationBiasResult {
  egger_p?: number | null;
  begg_p?: number | null;
  interpretation: string;
}

export interface LeaveOneOutResult {
  removed_study_id: string;
  pooled_effect: number;
  pooled_ci_low: number;
  pooled_ci_high: number;
  I2: number;
  delta_effect: number;
}

export interface SubgroupResult {
  subgroup: string;
  pooled_result: PooledResult;
  heterogeneity: HeterogeneityResult;
  studies: string[];
}

export interface PrismaPanelData {
  identified: number;
  screened: number;
  eligible: number;
  included: number;
  excluded_reasons: Array<{ study_id: string; reason: string }>;
}

export interface ArticleSections {
  abstract?: string | null;
  introduction?: string | null;
  methods?: string | null;
  results?: string | null;
  discussion?: string | null;
  conclusion?: string | null;
}

export interface EffectSizeRow {
  study_id: string;
  citation: string;
  effect_measure: string;
  effect: number;
  variance: number;
  standard_error: number;
  ci_low: number;
  ci_high: number;
  weight_fixed?: number;
  weight_random?: number;
  subgroup?: string;
}

export interface MetaAnalysisResponse {
  status: 'success' | 'warning' | 'error';
  project_id: string;
  question: string;
  effect_measure: string;
  model_used: string;
  studies_included: StudyExtraction[];
  studies_excluded: StudyExtraction[];
  effects_table: EffectSizeRow[];
  pooled_result?: PooledResult;
  heterogeneity?: HeterogeneityResult;
  publication_bias?: PublicationBiasResult;
  leave_one_out: LeaveOneOutResult[];
  subgroups: SubgroupResult[];
  forest_plot_svg?: string | null;
  funnel_plot_svg?: string | null;
  prisma: PrismaPanelData;
  narrative_results: string;
  article_sections: ArticleSections;
  warnings: string[];
}

export interface MetaUploadResponse {
  status: 'success' | 'warning' | 'error';
  project_id: string;
  studies: StudyExtraction[];
  notes: string[];
}

