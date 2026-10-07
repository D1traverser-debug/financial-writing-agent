import type { R2ArtifactStore, StoredObjectIdentity } from '../storage/r2-artifact-store.ts';

/** Phase-1 compatibility bridge only. The existing Python implementation remains authoritative. */
export interface PythonDeterministicDeliveryBridge {
  buildAndMechanicallyAuditDelivery(taskId:string):Promise<{
    artifacts:Record<string,StoredObjectIdentity>;
    renderPages:Record<string,StoredObjectIdentity[]>;
    mechanicalGate:'PASS'|'REVISE';
    evidence:string[];
  }>;
}

export class CompatibilityBridgeUnavailableError extends Error {}

export class DisabledPythonDeterministicDeliveryBridge implements PythonDeterministicDeliveryBridge {
  async buildAndMechanicallyAuditDelivery(_taskId:string):Promise<never>{
    throw new CompatibilityBridgeUnavailableError('Phase-1 Site PoC does not rewrite DOCX generation or LibreOffice/Poppler rendering. Configure the existing private Python deterministic-delivery/render service as the compatibility bridge before exercising DELIVERY.');
  }
}

export async function verifyBridgeOutputs(store:R2ArtifactStore, result:Awaited<ReturnType<PythonDeterministicDeliveryBridge['buildAndMechanicallyAuditDelivery']>>):Promise<void>{
  for(const item of Object.values(result.artifacts)) await store.readVerified(item);
  for(const pages of Object.values(result.renderPages)) for(const page of pages) await store.readVerified(page);
}
