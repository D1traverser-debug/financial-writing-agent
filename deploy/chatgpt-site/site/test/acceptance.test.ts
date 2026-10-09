import test from 'node:test';
import assert from 'node:assert/strict';
import { baseState } from './helpers.ts';
import { freezeAcceptanceContract } from '../src/runtime/acceptance.ts';

const candidate=(name:string,sections:string[])=>({name,rationale:'r',sections});
const sectionSpec=(title:string)=>({h1_title:title,directional_conclusion:`${title}-conclusion`,reader_gap:`${title}-gap`,payoff_requirement:`${title}-payoff`,logical_blocks:[`${title}-a`,`${title}-b`],h3_required_h2_indexes:[]});
const plan=(name:string,sections:string[])=>({candidates:[candidate(name,sections),candidate(name+'2',['x','y'])],selected_structure:candidate(name,sections),emphasis:['e'],side_focus_statement:'focus',company_selection_basis:['basis'],section_expectations:sections.map(sectionSpec),outline_fingerprint_refs:[],outline_collision_notes:[]});
const headline=(title:string)=>({title,angle:'a',finance_relevance:'f',factual_anchor:'anchor',primary_gap:'gap',opening_payoff:'payoff',cognitive_load:'low' as const});

test('DUAL initial acceptance freezes FINANCE_DEEP only',()=>{
  const s=baseState();
  s.stage='TITLE';
  const editorial={topic_dna:{},finance_deep:plan('deep',['D1','D2']),finance_broad:null,wechat_sticker:null};
  const headlines={finance_deep_candidates:[headline('DT')],finance_broad_candidates:[],finance_deep_selected:'DT',finance_broad_selected:null,wechat_sticker_candidates:[],wechat_sticker_selected:null};
  const contract=freezeAcceptanceContract(s,editorial,headlines);
  assert.deepEqual(contract.finance_deep?.expected_section_functions,['D1','D2']);
  assert.equal(contract.finance_deep?.section_expectations.length,2);
  assert.equal(contract.finance_broad,null);
  assert.equal(s.gates.acceptance_contract?.status,'PASS');
});

test('DUAL BROAD_DERIVATION preserves deep acceptance and freezes broad independently',()=>{
  const s=baseState();
  s.stage='TITLE';
  const deepEditorial={topic_dna:{},finance_deep:plan('deep',['D1','D2']),finance_broad:null,wechat_sticker:null};
  const deepHeadlines={finance_deep_candidates:[headline('DT')],finance_broad_candidates:[],finance_deep_selected:'DT',finance_broad_selected:null,wechat_sticker_candidates:[],wechat_sticker_selected:null};
  const deep=freezeAcceptanceContract(s,deepEditorial,deepHeadlines);

  s.stage='BROAD_DERIVATION';
  const broadEditorial={topic_dna:{},finance_deep:null,finance_broad:plan('broad',['B1','B2','B3']),wechat_sticker:null};
  const broadHeadlines={finance_deep_candidates:[],finance_broad_candidates:[headline('BT')],finance_deep_selected:null,finance_broad_selected:'BT',wechat_sticker_candidates:[],wechat_sticker_selected:null};
  const combined=freezeAcceptanceContract(s,broadEditorial,broadHeadlines);

  assert.deepEqual(combined.finance_deep,deep.finance_deep);
  assert.deepEqual(combined.finance_broad?.expected_section_functions,['B1','B2','B3']);
  assert.equal(combined.finance_broad?.section_expectations.length,3);
  assert.notDeepEqual(combined.finance_deep?.expected_section_functions,combined.finance_broad?.expected_section_functions);
});
