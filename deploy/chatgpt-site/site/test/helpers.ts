import type { D1DatabaseLike,D1PreparedStatementLike,D1RunResult } from '../src/storage/d1-state-store.ts';
import type { R2BucketLike,R2ObjectBodyLike } from '../src/storage/r2-artifact-store.ts';
import type { WritingState } from '../src/runtime/types.ts';

export function baseState(taskId='task-1'):WritingState { return { contract:{task_id:taskId,prompt:'x',source_refs:[],target_platforms:[],distribution_mode:'DUAL',content_mode:'FORMAL_ARTICLE',delivery_channel:'WORD_FILE_ONLY',visuals_enabled:false,visual_profile_ref:null,required_outputs:['AUDIT_DOCX','FINANCE_DEEP_DOCX','FINANCE_BROAD_DOCX'],run_constraints:{}}, stage:'INTAKE',checkpoint_version:0,gates:{knowledge_sync:{name:'knowledge_sync',status:'PASS',evidence:[],notes:'',updated_at:new Date().toISOString()}},artifacts:{},working:{},trace:[],attempts:{},blocked_reason:null,updated_at:new Date().toISOString() }; }

type Row={payload:string;version:number;updated_at:string};
export class MemoryD1 implements D1DatabaseLike {
  rows=new Map<string,Row>();
  prepare(sql:string):D1PreparedStatementLike { return new MemoryStmt(this,sql); }
}
class MemoryStmt implements D1PreparedStatementLike {
  values:unknown[]=[];
  readonly db:MemoryD1;
  readonly sql:string;
  constructor(db:MemoryD1,sql:string){ this.db=db; this.sql=sql; }
  bind(...values:unknown[]):D1PreparedStatementLike{this.values=values;return this;}
  async first<T>():Promise<T|null>{ if(this.sql.startsWith('SELECT payload')){ const row=this.db.rows.get(String(this.values[0])); return (row?{payload:row.payload,version:row.version}:null) as T|null;} throw new Error(`unsupported first: ${this.sql}`); }
  async all<T>():Promise<{results:T[]}>{ if(this.sql.startsWith('SELECT payload')){ const limit=Number(this.values[0]); const rows=[...this.db.rows.values()].sort((a,b)=>b.updated_at.localeCompare(a.updated_at)).slice(0,limit).map(r=>({payload:r.payload,version:r.version})); return {results:rows as T[]}; } throw new Error(`unsupported all: ${this.sql}`); }
  async run():Promise<D1RunResult>{
    if(this.sql.startsWith('INSERT')){ const [id,payload,updated,version]=this.values; const key=String(id); const existing=this.db.rows.get(key); if(existing && existing.version!==0) return {meta:{changes:0}}; this.db.rows.set(key,{payload:String(payload),updated_at:String(updated),version:Number(version)}); return {meta:{changes:1}}; }
    if(this.sql.startsWith('UPDATE')){ const [payload,updated,newVersion,id,expected]=this.values; const row=this.db.rows.get(String(id)); if(!row||row.version!==Number(expected)) return {meta:{changes:0}}; this.db.rows.set(String(id),{payload:String(payload),updated_at:String(updated),version:Number(newVersion)}); return {meta:{changes:1}}; }
    throw new Error(`unsupported run: ${this.sql}`);
  }
}
export class MemoryR2 implements R2BucketLike { objects=new Map<string,Uint8Array>(); async put(key:string,value:ArrayBuffer|Uint8Array):Promise<void>{ this.objects.set(key,value instanceof Uint8Array?new Uint8Array(value):new Uint8Array(value)); } async get(key:string):Promise<R2ObjectBodyLike|null>{ const b=this.objects.get(key); if(!b)return null; const copy=new Uint8Array(b); return {size:copy.byteLength,arrayBuffer:async()=>copy.buffer.slice(copy.byteOffset,copy.byteOffset+copy.byteLength)}; } }
