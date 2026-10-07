export const STAGES = ['INTAKE','RESEARCH','RESEARCH_AUDIT','EDITORIAL','TITLE','DRAFT','EDITORIAL_AUDIT','DELIVERY','MECHANICAL_AUDIT','FINAL_AUDIT','COMPLETE','BLOCKED'] as const;
export type Stage = (typeof STAGES)[number];
export type GateStatus = 'NOT_RUN'|'PASS'|'REVISE'|'FAIL'|'N_A';
export type DistributionMode = 'FINANCE_DEEP'|'FINANCE_BROAD'|'DUAL';
export type ContentMode = 'FORMAL_ARTICLE'|'WECHAT_STICKER_POST';
export type DeliveryChannel = 'WORD_FILE_ONLY'|'CHAT_TEXT';
export type ArtifactKind = 'FINANCE_DEEP_DOCX'|'FINANCE_BROAD_DOCX'|'WECHAT_STICKER_DOCX'|'AUDIT_DOCX'|'VISUAL_MANIFEST_JSON'|'CHAT_TEXT';

export interface GateRecord { name:string; status:GateStatus; evidence:string[]; notes:string; updated_at:string; }
export interface ArtifactRecord { kind:ArtifactKind; object_key:string; exists:boolean; sha256:string|null; mime_type?:string; size?:number; }
export interface TaskContract {
  task_id:string; prompt:string; source_refs:string[]; target_platforms:string[]; distribution_mode:DistributionMode; content_mode:ContentMode; delivery_channel:DeliveryChannel; visuals_enabled:boolean; visual_profile_ref:string|null; required_outputs:ArtifactKind[]; run_constraints:Record<string,unknown>;
}
export interface TraceEvent { seq:number; stage:Stage; event:string; detail:string; at:string; }
export interface WritingState {
  contract:TaskContract; stage:Stage; checkpoint_version:number; gates:Record<string,GateRecord>; artifacts:Partial<Record<ArtifactKind,ArtifactRecord>>; working:Record<string,unknown>; trace:TraceEvent[]; attempts:Record<string,number>; blocked_reason:string|null; updated_at:string;
}
export interface StructureCandidate { name:string; rationale:string; sections:string[]; }
export interface ModeEditorialPlan { candidates:StructureCandidate[]; selected_structure:StructureCandidate; emphasis:string[]; side_focus_statement:string; company_selection_basis:string[]; outline_fingerprint_refs:string[]; outline_collision_notes:string[]; }
export interface HeadlineCandidate { title:string; angle:string; finance_relevance:string; factual_anchor:string; primary_gap:string; opening_payoff:string; cognitive_load:'low'|'medium'|'high'; }
export interface EditorialPlan { topic_dna:Record<string,unknown>; finance_deep?:ModeEditorialPlan|null; finance_broad?:ModeEditorialPlan|null; wechat_sticker?:ModeEditorialPlan|null; }
export interface HeadlinePackage { finance_deep_candidates:HeadlineCandidate[]; finance_broad_candidates:HeadlineCandidate[]; finance_deep_selected:string|null; finance_broad_selected:string|null; wechat_sticker_candidates:HeadlineCandidate[]; wechat_sticker_selected:string|null; }
export interface ModeAcceptanceContract { selected_title:string; headline_factual_anchor:string; headline_primary_gap:string; headline_opening_payoff:string; selected_structure_name:string; expected_h1_count:number; expected_section_functions:string[]; lead_required:1; side_focus_statement:string; company_selection_basis:string[]; }
export interface WritingAcceptanceContract { finance_deep:ModeAcceptanceContract|null; finance_broad:ModeAcceptanceContract|null; wechat_sticker:ModeAcceptanceContract|null; required_outputs:string[]; delivery_channel:DeliveryChannel; visuals_enabled:boolean; }

export function nowIso(): string { return new Date().toISOString(); }
export function addTrace(state:WritingState,event:string,detail=''):void { const at=nowIso(); state.trace.push({seq:state.trace.length+1,stage:state.stage,event,detail,at}); state.updated_at=at; }
export function setGate(state:WritingState,name:string,status:GateStatus,evidence:string[]=[],notes=''):void { const updated_at=nowIso(); state.gates[name]={name,status,evidence,notes,updated_at}; state.updated_at=updated_at; }
