import {
  createMcpHandler,
  McpServer,
  type CallToolResult,
  type ListToolsResult,
  type Tool,
} from '@modelcontextprotocol/server';
import { RESOURCE_CONTRACTS, TOOL_CONTRACTS } from './contract-registry.ts';

export interface ToolDispatcher { call(name:string,args:Record<string,unknown>):Promise<CallToolResult>; }
export interface ResourceDispatcher { read(uri:string):Promise<{mimeType:string;bytes:Uint8Array}>; }
export class FailClosedDispatcher implements ToolDispatcher,ResourceDispatcher {
  async call(name:string,_args:Record<string,unknown>={}):Promise<{isError:true;content:Array<{type:'text';text:string}>}>{ return {isError:true,content:[{type:'text',text:`Phase-1 compatibility layer exposes the frozen contract but tool execution is not enabled for ${name} until behavioral parity wiring is complete.`}]}; }
  async read(uri:string):Promise<never>{ throw new Error(`Phase-1 resource execution is not enabled until D1/R2 task metadata wiring is complete: ${uri}`); }
}

export function createFinancialWritingMcpServer(dispatcher:ToolDispatcher & ResourceDispatcher = new FailClosedDispatcher()):McpServer {
  const server=new McpServer({name:'Financial Writing Agent',version:'0.2.1-site-poc'},{capabilities:{tools:{},resources:{}}});
  server.server.setRequestHandler('tools/list', async():Promise<ListToolsResult>=>({tools:TOOL_CONTRACTS.map(tool=>({name:tool.name,title:tool.title,description:tool.description,inputSchema:tool.inputSchema as Tool['inputSchema'],outputSchema:tool.outputSchema as Tool['outputSchema'],annotations:tool.annotations,_meta:Object.keys(tool.meta).length?tool.meta:undefined}))}));
  server.server.setRequestHandler('tools/call', async(request:any)=>{
    const tool=TOOL_CONTRACTS.find(item=>item.name===request.params?.name);
    if(!tool) throw new Error(`unknown tool: ${String(request.params?.name)}`);
    return dispatcher.call(tool.name,(request.params?.arguments ?? {}) as Record<string,unknown>);
  });
  server.server.setRequestHandler('resources/templates/list', async()=>({resourceTemplates:RESOURCE_CONTRACTS.map(resource=>({uriTemplate:resource.uriTemplate,name:resource.uriTemplate,mimeType:resource.mimeType}))}));
  server.server.setRequestHandler('resources/read', async(request:any)=>{ const uri=String(request.params?.uri ?? ''); const result=await dispatcher.read(uri); return {contents:[{uri,mimeType:result.mimeType,blob:bytesToBase64(result.bytes)}]}; });
  return server;
}
function bytesToBase64(bytes:Uint8Array):string { let binary=''; for(const b of bytes) binary+=String.fromCharCode(b); return btoa(binary); }

export function createFinancialWritingMcpHandler(factory:()=>ToolDispatcher & ResourceDispatcher){ return createMcpHandler(()=>createFinancialWritingMcpServer(factory())); }
