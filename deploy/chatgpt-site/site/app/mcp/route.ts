import { env } from 'cloudflare:workers';
import { createFinancialWritingMcpHandler } from '../../src/mcp/server.ts';
import { SiteDispatcher } from '../../src/mcp/site-dispatcher.ts';

async function handle(request:Request):Promise<Response>{
  if(!env.DB || typeof env.DB.prepare!=='function'){
    throw new Error('Missing Site D1 binding: DB');
  }
  if(!env.FILES || typeof env.FILES.get!=='function' || typeof env.FILES.put!=='function'){
    throw new Error('Missing Site R2 binding: FILES');
  }

  const handler=createFinancialWritingMcpHandler(
    ()=>new SiteDispatcher(env.DB,env.FILES),
  );
  return handler.fetch(request);
}

export async function POST(request:Request):Promise<Response>{ return handle(request); }
export async function GET(request:Request):Promise<Response>{ return handle(request); }
export async function DELETE(request:Request):Promise<Response>{ return handle(request); }
