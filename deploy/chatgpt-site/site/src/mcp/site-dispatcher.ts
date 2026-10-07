import type { D1DatabaseLike } from '../storage/d1-state-store.ts';
import { D1StateStore } from '../storage/d1-state-store.ts';
import type { R2BucketLike } from '../storage/r2-artifact-store.ts';
import { R2ArtifactStore } from '../storage/r2-artifact-store.ts';
import { R2ResourceDispatcher } from './r2-resource-dispatcher.ts';
import { FailClosedDispatcher, type ResourceDispatcher, type ToolDispatcher } from './server.ts';

/** Phase-1 wiring: D1/R2 resource reads are live; business tool execution remains fail-closed until behavioral parity wiring is complete. */
export class SiteDispatcher implements ToolDispatcher, ResourceDispatcher {
  private readonly tools=new FailClosedDispatcher();
  private readonly resources:R2ResourceDispatcher;
  constructor(db:D1DatabaseLike,bucket:R2BucketLike){ this.resources=new R2ResourceDispatcher(new D1StateStore(db),new R2ArtifactStore(bucket)); }
  call(name:string,args:Record<string,unknown>){ return this.tools.call(name,args); }
  read(uri:string){ return this.resources.read(uri); }
}
