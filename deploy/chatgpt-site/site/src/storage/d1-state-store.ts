import type { WritingState } from '../runtime/types.ts';

export class StateConflictError extends Error {}

export interface D1RunResult { meta?: { changes?: number }; success?: boolean; }
export interface D1PreparedStatementLike {
  bind(...values: unknown[]): D1PreparedStatementLike;
  first<T=Record<string,unknown>>(): Promise<T|null>;
  all<T=Record<string,unknown>>(): Promise<{results:T[]}>;
  run(): Promise<D1RunResult>;
}
export interface D1DatabaseLike { prepare(sql:string): D1PreparedStatementLike; }

export class D1StateStore {
  private readonly db:D1DatabaseLike;
  constructor(db:D1DatabaseLike) { this.db=db; }

  async save(state:WritingState):Promise<void> {
    const previousVersion=state.checkpoint_version;
    const newVersion=previousVersion+1;
    const persisted:WritingState={...state, checkpoint_version:newVersion};
    const payload=JSON.stringify(persisted);
    let result:D1RunResult;
    if(previousVersion===0){
      result=await this.db.prepare('INSERT INTO runs(task_id,payload,updated_at,version) VALUES(?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at, version=excluded.version WHERE runs.version=0').bind(state.contract.task_id,payload,state.updated_at,newVersion).run();
    } else {
      result=await this.db.prepare('UPDATE runs SET payload=?, updated_at=?, version=? WHERE task_id=? AND version=?').bind(payload,state.updated_at,newVersion,state.contract.task_id,previousVersion).run();
    }
    if((result.meta?.changes ?? 0)!==1){
      throw new StateConflictError(`stale checkpoint for ${state.contract.task_id}: state_version=${previousVersion}`);
    }
    state.checkpoint_version=newVersion;
  }

  async load(taskId:string):Promise<WritingState|null>{
    const row=await this.db.prepare('SELECT payload, version FROM runs WHERE task_id=?').bind(taskId).first<{payload:string;version:number}>();
    if(!row) return null;
    const state=JSON.parse(row.payload) as WritingState;
    state.checkpoint_version=Number(row.version);
    return state;
  }

  async listRecent(limit=10):Promise<WritingState[]>{
    const safe=Math.max(1,Math.min(Math.trunc(limit),100));
    const rows=await this.db.prepare('SELECT payload, version FROM runs ORDER BY updated_at DESC LIMIT ?').bind(safe).all<{payload:string;version:number}>();
    return rows.results.map(row=>{ const state=JSON.parse(row.payload) as WritingState; state.checkpoint_version=Number(row.version); return state; });
  }
}
