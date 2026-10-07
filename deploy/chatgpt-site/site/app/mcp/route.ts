import { env } from 'cloudflare:workers';
import { createFinancialWritingMcpHandler } from '../../src/mcp/server.ts';
import { SiteDispatcher } from '../../src/mcp/site-dispatcher.ts';

const handler=createFinancialWritingMcpHandler(()=>new SiteDispatcher(env.DB,env.FILES));
export async function POST(request:Request):Promise<Response>{ return handler.fetch(request); }
export async function GET(request:Request):Promise<Response>{ return handler.fetch(request); }
export async function DELETE(request:Request):Promise<Response>{ return handler.fetch(request); }
