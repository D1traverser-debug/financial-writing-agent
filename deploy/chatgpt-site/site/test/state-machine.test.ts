import test from 'node:test';
import assert from 'node:assert/strict';
import { baseState } from './helpers.ts';
import { BASE_COMPLETION_GATES, block, invalidateForRevision, requiredCompletionGates, requiredFinalEvidenceKeys, resumeFromBlocked, transition, WorkflowError } from '../src/runtime/state-machine.ts';

test('state transition parity: legal and illegal transitions',()=>{
  const state=baseState();
  transition(state,'RESEARCH');
  assert.equal(state.stage,'RESEARCH');
  assert.throws(()=>transition(state,'TITLE'),WorkflowError);
});

test('DUAL deep draft can only reach audit through BROAD_DERIVATION in the legal phased path',()=>{
  const state=baseState();
  state.stage='DRAFT';
  transition(state,'BROAD_DERIVATION');
  assert.equal(state.stage,'BROAD_DERIVATION');
  transition(state,'EDITORIAL_AUDIT');
  assert.equal(state.stage,'EDITORIAL_AUDIT');
});

test('BROAD_DERIVATION survives BLOCKED recovery',()=>{
  const state=baseState();
  state.stage='BROAD_DERIVATION';
  block(state,'dependency failed');
  assert.equal(state.stage,'BLOCKED');
  assert.equal(state.working.blocked_from_stage,'BROAD_DERIVATION');
  resumeFromBlocked(state);
  assert.equal(state.stage,'BROAD_DERIVATION');
  assert.equal(state.blocked_reason,null);
});

test('BLOCKED recovery returns only to recorded origin',()=>{
  const state=baseState();
  transition(state,'RESEARCH');
  block(state,'dependency failed');
  assert.equal(state.stage,'BLOCKED');
  assert.equal(state.working.blocked_from_stage,'RESEARCH');
  resumeFromBlocked(state);
  assert.equal(state.stage,'RESEARCH');
  assert.equal(state.blocked_reason,null);
  assert.equal(state.working.blocked_from_stage,undefined);
});

test('revision invalidation resets broad derivation and downstream artifacts',()=>{
  const state=baseState();
  state.stage='FINAL_AUDIT';
  for(const gate of ['draft_output','broad_derivation','style_audit','editorial_audit','delivery_output','mechanical_audit','final_audit']){
    state.gates[gate]={name:gate,status:'PASS',evidence:['x'],notes:'',updated_at:state.updated_at};
  }
  state.working.broad_derivation_phase='COMPLETE';
  state.working.dual_derivation_receipt={ok:true};
  state.artifacts.FINANCE_DEEP_DOCX={kind:'FINANCE_DEEP_DOCX',object_key:'x',exists:true,sha256:'abc'};
  state.artifacts.VISUAL_MANIFEST_JSON={kind:'VISUAL_MANIFEST_JSON',object_key:'v',exists:true,sha256:'def'};
  state.working.render_manifest={x:['p']};
  invalidateForRevision(state,'DRAFT','repair');
  for(const gate of ['draft_output','broad_derivation','style_audit','editorial_audit','delivery_output','mechanical_audit','final_audit']) assert.equal(state.gates[gate]?.status,'NOT_RUN');
  assert.equal(state.gates.knowledge_sync?.status,'NOT_RUN');
  assert.equal(state.working.broad_derivation_phase,'WAITING_FOR_DEEP');
  assert.equal(state.working.dual_derivation_receipt,undefined);
  assert.equal(state.artifacts.FINANCE_DEEP_DOCX,undefined);
  assert.equal(state.artifacts.VISUAL_MANIFEST_JSON,undefined);
  assert.equal(state.working.render_manifest,undefined);
});

test('mandatory completion inventory adds broad_derivation only for formal DUAL',()=>{
  const dual=baseState();
  assert.equal(BASE_COMPLETION_GATES.size,14);
  assert.equal(requiredCompletionGates(dual).size,15);
  assert.equal(requiredCompletionGates(dual).has('broad_derivation'),true);

  const deep=baseState();
  deep.contract.distribution_mode='FINANCE_DEEP';
  assert.deepEqual([...requiredCompletionGates(deep)].sort(),[...BASE_COMPLETION_GATES].sort());

  deep.contract.visuals_enabled=true;
  assert.equal(requiredCompletionGates(deep).has('visual_assets'),true);
});

test('final evidence parity includes global integrity, current formal criteria and DUAL derivation proof',()=>{
  const state=baseState();
  state.working.acceptance_contract={
    finance_deep:{selected_title:'D',headline_factual_anchor:'a',headline_primary_gap:'g',headline_opening_payoff:'p',selected_structure_name:'deep',expected_h1_count:1,expected_section_functions:['D1'],section_expectations:[{h1_title:'D1',directional_conclusion:'c',reader_gap:'g',payoff_requirement:'p',logical_blocks:['a'],h3_required_h2_indexes:[]}],lead_required:1,side_focus_statement:'s',company_selection_basis:['b']},
    finance_broad:{selected_title:'B',headline_factual_anchor:'a',headline_primary_gap:'g',headline_opening_payoff:'p',selected_structure_name:'broad',expected_h1_count:1,expected_section_functions:['B1'],section_expectations:[{h1_title:'B1',directional_conclusion:'c',reader_gap:'g',payoff_requirement:'p',logical_blocks:['a'],h3_required_h2_indexes:[]}],lead_required:1,side_focus_statement:'s',company_selection_basis:['b']},
    wechat_sticker:null,
    required_outputs:['AUDIT_DOCX','FINANCE_DEEP_DOCX','FINANCE_BROAD_DOCX'],
    delivery_channel:'WORD_FILE_ONLY',
    visuals_enabled:false,
  };
  const keys=requiredFinalEvidenceKeys(state);
  for(const key of ['GLOBAL.source_completion','GLOBAL.time_integrity','FINANCE_DEEP.hook_quality','FINANCE_BROAD.stock_judgment_clarity','FINANCE_DEEP.H1_1.promise_payoff','FINANCE_BROAD.H1_1.promise_payoff','DUAL.deep_master_quality','DUAL.broad_derivation_fidelity','DUAL.broad_hook_strength']) assert.equal(keys.has(key),true,key);
});
