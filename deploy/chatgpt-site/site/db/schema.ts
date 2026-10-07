import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';
export const runs = sqliteTable('runs', {
  taskId: text('task_id').primaryKey(),
  payload: text('payload').notNull(),
  updatedAt: text('updated_at').notNull(),
  version: integer('version').notNull().default(0),
});
