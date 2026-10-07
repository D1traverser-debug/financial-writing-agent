import type { WritingState } from '../runtime/types.ts';
import type { D1StateStore } from '../storage/d1-state-store.ts';
import { R2ArtifactStore, type StoredObjectIdentity } from '../storage/r2-artifact-store.ts';
import type { ResourceDispatcher } from './server.ts';

const DOCX='application/vnd.openxmlformats-officedocument.wordprocessingml.document';
export class R2ResourceDispatcher implements ResourceDispatcher {
  private readonly states:D1StateStore;
  private readonly objects:R2ArtifactStore;
  constructor(states:D1StateStore,objects:R2ArtifactStore){ this.states=states; this.objects=objects; }
  async read(uri:string):Promise<{mimeType:string;bytes:Uint8Array}>{
    const parsed=parseResourceUri(uri); const state=await this.states.load(parsed.taskId); if(!state) throw new Error(`task not found: ${parsed.taskId}`);
    if(parsed.family==='render') return this.readRender(state,parsed.kind,parsed.page!);
    const artifact=(state.artifacts as any)[parsed.kind] as {object_key:string;sha256:string;size:number;mime_type?:string;exists:boolean}|undefined;
    if(!artifact?.exists||!artifact.sha256) throw new Error(`artifact not available or unidentified: ${parsed.kind}`);
    const identity:StoredObjectIdentity={object_key:artifact.object_key,sha256:artifact.sha256,size:Number(artifact.size),mime_type:artifact.mime_type ?? parsed.mimeType};
    return {mimeType:identity.mime_type,bytes:await this.objects.readVerified(identity)};
  }
  private async readRender(state:WritingState,kind:string,page:number):Promise<{mimeType:string;bytes:Uint8Array}>{
    const manifest=(state.working.render_manifest ?? {}) as Record<string,StoredObjectIdentity[]>; const pages=manifest[kind]; if(!pages||page<1||page>pages.length) throw new Error(`render page out of range: ${kind} page ${page}`); const identity=pages[page-1]!; return {mimeType:'image/png',bytes:await this.objects.readVerified(identity)};
  }
}
function parseResourceUri(uri:string):{family:'artifact'|'render';taskId:string;kind:string;page?:number;mimeType:string}{
  let m=/^writing-docx:\/\/([^/]+)\/([^/]+)$/.exec(uri); if(m) return {family:'artifact',taskId:m[1]!,kind:m[2]!,mimeType:DOCX};
  m=/^writing-json:\/\/([^/]+)\/([^/]+)$/.exec(uri); if(m) return {family:'artifact',taskId:m[1]!,kind:m[2]!,mimeType:'application/json'};
  m=/^writing-text:\/\/([^/]+)\/([^/]+)$/.exec(uri); if(m) return {family:'artifact',taskId:m[1]!,kind:m[2]!,mimeType:'text/plain; charset=utf-8'};
  m=/^writing-render:\/\/([^/]+)\/([^/]+)\/(\d+)$/.exec(uri); if(m) return {family:'render',taskId:m[1]!,kind:m[2]!,page:Number(m[3]),mimeType:'image/png'};
  throw new Error(`unsupported resource URI: ${uri}`);
}
