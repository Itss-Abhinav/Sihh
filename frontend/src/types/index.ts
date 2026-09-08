export type Role = 'CONSUMER' | 'RETAILER' | 'INSPECTOR' | 'ADMIN';

export type ComplianceStatus = 
  | 'PASS' 
  | 'FAIL' 
  | 'NOT_APPLICABLE' 
  | 'UNABLE_TO_VERIFY' 
  | 'REQUIRES_VERIFICATION';

export type OverallStatus = 
  | 'COMPLIANT' 
  | 'POTENTIAL_ISSUES_DETECTED' 
  | 'PARTIALLY_VERIFIED' 
  | 'UNABLE_TO_VERIFY';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface RuleCheckResult {
  field: string;
  status: ComplianceStatus;
  detectedValue?: string | null;
  expectedRequirement: string;
  explanation: string;
  ruleCode: string;
  sourceReference: string;
  category: string;
  penaltyNote?: string | null;
}

export interface ExtractedField {
  value?: string | null;
  confidence: number;
  sourceText?: string | null;
}

export interface ExtractedData {
  productName?: ExtractedField;
  brandName?: ExtractedField;
  productCategory?: ExtractedField;
  genericName?: ExtractedField;
  mrp?: ExtractedField;
  netQuantity?: ExtractedField;
  quantityUnit?: ExtractedField;
  manufacturerName?: ExtractedField;
  manufacturerAddress?: ExtractedField;
  packerName?: ExtractedField;
  packerAddress?: ExtractedField;
  importerName?: ExtractedField;
  importerAddress?: ExtractedField;
  manufactureDate?: ExtractedField;
  importDate?: ExtractedField;
  consumerCareName?: ExtractedField;
  consumerCarePhone?: ExtractedField;
  consumerCareEmail?: ExtractedField;
  consumerCareAddress?: ExtractedField;
  countryOfOrigin?: ExtractedField;
  unitSalePrice?: ExtractedField;
  sizeDimensions?: ExtractedField;
  rawOcrText?: string;
}

export interface ScanSummaryItem {
  id: string;
  productName?: string;
  brandName?: string;
  category?: string;
  overallStatus: OverallStatus;
  failedCount: number;
  passedCount: number;
  createdAt: string;
}

export interface ScanDetailResponse {
  id: string;
  userId?: string | null;
  productName?: string | null;
  brandName?: string | null;
  category?: string | null;
  overallStatus: OverallStatus;
  imageUrl?: string | null;
  createdAt: string;
  disclaimer: string;
  summary: {
    total: number;
    passed: number;
    failed: number;
    requires_verification?: number;
    unable_to_verify: number;
    not_applicable: number;
  };
  extractedData: Record<string, any>;
  rawOcrText: string;
  checks: RuleCheckResult[];
  executionTimeMs: number;
}

export interface AdminViolationMetric {
  ruleCode: string;
  ruleName: string;
  occurrenceCount: number;
  category: string;
}

export interface CategoryMetric {
  category: string;
  count: number;
}

export interface AdminDashboardStats {
  totalScans: number;
  compliantScans: number;
  potentialIssueScans: number;
  partiallyVerifiedScans: number;
  unableToVerifyScans: number;
  complianceRatePct: number;
  commonPotentialViolations: AdminViolationMetric[];
  categoryDistribution: CategoryMetric[];
  recentScans: ScanSummaryItem[];
  neutralNotice: string;
}