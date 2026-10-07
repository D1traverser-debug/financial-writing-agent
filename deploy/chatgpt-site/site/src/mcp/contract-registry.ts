import { PYTHON_CONTRACT_SNAPSHOT as snapshot } from './python-contract-snapshot.ts';

export type JsonSchema = Record<string,unknown>;
export interface ToolContract {
  name:string; title:string; description:string;
  annotations:{readOnlyHint:boolean;destructiveHint:boolean;openWorldHint:boolean;idempotentHint:boolean};
  inputSchema:JsonSchema; outputSchema:JsonSchema; meta:Record<string,unknown>;
}
export interface ResourceContract { uriTemplate:string; mimeType:string; }

type RawTool = Omit<ToolContract,'inputSchema'|'outputSchema'> & {inputSchemaRef:string;outputSchemaRef:string};
const schemas=snapshot.schemas as Record<string,JsonSchema>;
export const TOOL_CONTRACTS:readonly ToolContract[]=(snapshot.tools as RawTool[]).map(tool=>({
  ...tool,
  inputSchema:schemas[tool.inputSchemaRef]!,
  outputSchema:schemas[tool.outputSchemaRef]!,
}));
export const RESOURCE_CONTRACTS:readonly ResourceContract[]=snapshot.resources as ResourceContract[];
export const PYTHON_ORACLE=snapshot.oracle;

if(TOOL_CONTRACTS.length!==16) throw new Error(`contract snapshot must expose exactly 16 tools, found ${TOOL_CONTRACTS.length}`);
