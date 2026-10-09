import { setGate, type EditorialPlan, type HeadlineCandidate, type HeadlinePackage, type ModeAcceptanceContract, type ModeEditorialPlan, type WritingAcceptanceContract, type WritingState } from './types.ts';

function selectedCandidate(candidates:HeadlineCandidate[],selected:string):HeadlineCandidate {
  const matches=candidates.filter(candidate=>candidate.title===selected);
  if(matches.length!==1) throw new Error('selected headline must identify exactly one candidate');
  return matches[0]!;
}

function modeContract(plan:ModeEditorialPlan,title:string,candidate:HeadlineCandidate):ModeAcceptanceContract {
  return {
    selected_title:title,
    headline_factual_anchor:candidate.factual_anchor,
    headline_primary_gap:candidate.primary_gap,
    headline_opening_payoff:candidate.opening_payoff,
    selected_structure_name:plan.selected_structure.name,
    expected_h1_count:plan.selected_structure.sections.length,
    expected_section_functions:[...plan.selected_structure.sections],
    section_expectations:[...(plan.section_expectations ?? [])],
    lead_required:1,
    side_focus_statement:plan.side_focus_statement,
    company_selection_basis:[...plan.company_selection_basis],
  };
}

function priorAcceptance(state:WritingState):WritingAcceptanceContract|null {
  const raw=state.working.acceptance_contract;
  if(!raw || typeof raw!=='object') return null;
  return raw as WritingAcceptanceContract;
}

export function freezeAcceptanceContract(state:WritingState, editorial:EditorialPlan, headlines:HeadlinePackage):WritingAcceptanceContract {
  let finance_deep:ModeAcceptanceContract|null=null;
  let finance_broad:ModeAcceptanceContract|null=null;
  let wechat_sticker:ModeAcceptanceContract|null=null;
  let phase='INITIAL';

  if(state.contract.content_mode==='WECHAT_STICKER_POST'){
    if(!editorial.wechat_sticker||!headlines.wechat_sticker_selected) throw new Error('WECHAT_STICKER_POST acceptance contract requires frozen editorial plan and selected title');
    wechat_sticker=modeContract(editorial.wechat_sticker,headlines.wechat_sticker_selected,selectedCandidate(headlines.wechat_sticker_candidates,headlines.wechat_sticker_selected));
  } else if(state.contract.distribution_mode==='FINANCE_DEEP'){
    if(!editorial.finance_deep||!headlines.finance_deep_selected) throw new Error('FINANCE_DEEP acceptance contract requires frozen editorial plan and selected title');
    finance_deep=modeContract(editorial.finance_deep,headlines.finance_deep_selected,selectedCandidate(headlines.finance_deep_candidates,headlines.finance_deep_selected));
  } else if(state.contract.distribution_mode==='FINANCE_BROAD'){
    if(!editorial.finance_broad||!headlines.finance_broad_selected) throw new Error('FINANCE_BROAD acceptance contract requires frozen editorial plan and selected title');
    finance_broad=modeContract(editorial.finance_broad,headlines.finance_broad_selected,selectedCandidate(headlines.finance_broad_candidates,headlines.finance_broad_selected));
  } else if(state.stage==='BROAD_DERIVATION'){
    phase='BROAD_DERIVATION';
    const prior=priorAcceptance(state);
    if(!prior?.finance_deep) throw new Error('DUAL broad derivation requires a previously frozen FINANCE_DEEP acceptance contract');
    if(!editorial.finance_broad||!headlines.finance_broad_selected) throw new Error('DUAL broad derivation requires FINANCE_BROAD editorial plan and selected title');
    finance_deep=prior.finance_deep;
    finance_broad=modeContract(editorial.finance_broad,headlines.finance_broad_selected,selectedCandidate(headlines.finance_broad_candidates,headlines.finance_broad_selected));
  } else {
    phase='DEEP_MASTER';
    if(!editorial.finance_deep||!headlines.finance_deep_selected) throw new Error('DUAL initial acceptance freezes FINANCE_DEEP before FINANCE_BROAD derivation');
    finance_deep=modeContract(editorial.finance_deep,headlines.finance_deep_selected,selectedCandidate(headlines.finance_deep_candidates,headlines.finance_deep_selected));
  }

  const contract:WritingAcceptanceContract={
    finance_deep,
    finance_broad,
    wechat_sticker,
    required_outputs:[...state.contract.required_outputs],
    delivery_channel:state.contract.delivery_channel,
    visuals_enabled:state.contract.visuals_enabled,
  };
  state.working.acceptance_contract=contract;
  setGate(state,'acceptance_contract','PASS',[
    `phase=${phase}`,
    `required_outputs=${contract.required_outputs.length}`,
    `finance_deep=${finance_deep?'yes':'no'}`,
    `finance_broad=${finance_broad?'yes':'no'}`,
    `wechat_sticker=${wechat_sticker?'yes':'no'}`,
    'selected headline factual anchor/gap/opening payoff frozen per applicable phase',
  ]);
  return contract;
}
