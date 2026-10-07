export class ArtifactChecksumMismatchError extends Error {}
export class ArtifactMissingError extends Error {}

export interface R2ObjectBodyLike { arrayBuffer():Promise<ArrayBuffer>; size?:number; httpMetadata?:{contentType?:string}; customMetadata?:Record<string,string>; }
export interface R2BucketLike { put(key:string,value:ArrayBuffer|Uint8Array,options?:{httpMetadata?:{contentType?:string};customMetadata?:Record<string,string>}):Promise<unknown>; get(key:string):Promise<R2ObjectBodyLike|null>; }
export interface StoredObjectIdentity { object_key:string; sha256:string; size:number; mime_type:string; }

async function sha256(bytes:Uint8Array):Promise<string>{ const copy=new Uint8Array(bytes); const digest=await crypto.subtle.digest('SHA-256',copy.buffer); return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join(''); }

export class R2ArtifactStore {
  private readonly bucket:R2BucketLike;
  constructor(bucket:R2BucketLike) { this.bucket=bucket; }
  static artifactKey(taskId:string,fileName:string):string { return `tasks/${taskId}/artifacts/${fileName}`; }
  static renderKey(taskId:string,kind:string,page:number):string { return `tasks/${taskId}/renders/${kind}/page-${String(page).padStart(4,'0')}.png`; }
  static assetKey(taskId:string,fileName:string):string { return `tasks/${taskId}/assets/${fileName}`; }

  async putVerified(key:string,bytes:Uint8Array,mimeType:string):Promise<StoredObjectIdentity>{
    const hash=await sha256(bytes);
    await this.bucket.put(key,bytes,{httpMetadata:{contentType:mimeType},customMetadata:{sha256:hash}});
    const identity={object_key:key,sha256:hash,size:bytes.byteLength,mime_type:mimeType};
    await this.readVerified(identity);
    return identity;
  }

  async readVerified(identity:StoredObjectIdentity):Promise<Uint8Array>{
    const object=await this.bucket.get(identity.object_key);
    if(!object) throw new ArtifactMissingError(`artifact missing: ${identity.object_key}`);
    const bytes=new Uint8Array(await object.arrayBuffer());
    const actual=await sha256(bytes);
    if(actual!==identity.sha256) throw new ArtifactChecksumMismatchError(`artifact checksum mismatch: ${identity.object_key}; expected=${identity.sha256}; actual=${actual}`);
    if(bytes.byteLength!==identity.size) throw new ArtifactChecksumMismatchError(`artifact size mismatch: ${identity.object_key}; expected=${identity.size}; actual=${bytes.byteLength}`);
    return bytes;
  }
}
