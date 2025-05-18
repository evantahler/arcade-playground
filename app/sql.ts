import Arcade from "@arcadeai/arcadejs";
import OpenAI from 'openai';

const ARCADE_API_KEY = Bun.env.ARCADE_API_KEY;
const OPEN_AI_API_KEY = Bun.env.OPENAI_API_KEY;
const USER_ID = Bun.env.USER_ID;
const DB_DIALECT = "POSTGRES"; 
const SCHEMA_NAME = "public"; 

const SYSTEM_PROMPT = `
You are an expert SQL analyst.
For all questions, you will use only the information provided to you to answer the question, and no prior knowledge.
The SQL dialect is "${DB_DIALECT}".
ONLY RESPOND WITH A SQL STATEMENT AND NOTHING ELSE, ALL ON A SINGLE LINE.  DO NOT EXPLAIN THE SQL STATEMENT.  DO NOT FORMAT THE SQL STATEMENT IN MARKDOWN.  DO NOT ADD ANYTHING ELSE TO THE RESPONSE.
`;

const ArcadeClient = new Arcade({
  apiKey: ARCADE_API_KEY,
});

const OpenAIClient = new OpenAI({
  apiKey: OPEN_AI_API_KEY
});

const sqlTools = await ArcadeClient.tools.formatted.list({
  format: "openai",
  toolkit: "sql",
});

console.log("⚙️ Found the following tools:");
sqlTools.items.forEach((tool) => {
  // @ts-ignore
  console.log(`${tool.function.name}: ${tool.function.description}`);
});

const response = await ArcadeClient.tools.execute({
  tool_name: "Sql.DiscoverTables",
  user_id: USER_ID,
  input: {
    schema_name: SCHEMA_NAME,
  },
});
const tables = response.output?.value as string[]
console.log(`\r\n[🔍] Discoverd the following tables: ${tables.join(', ')}`);

const schemas: Record<string, any> = {};
for (const table of tables) {
  const response = await ArcadeClient.tools.execute({
    tool_name: "Sql.GetTableSchema",
    user_id: USER_ID,
    input: {
      schema_name: SCHEMA_NAME,
      table_name: table,
    },
  });
  const schema = response.output?.value as string;
  schemas[table]= schema;
  console.log(`[📜] Schema for ${table}: ${schema}`);
}


// /* --- EXAMPLES --- */
await buildQueryAndExecute("Get the first 10 users's IDs and Names", schemas);
await buildQueryAndExecute("Who has sent the most chat messages?", schemas);

// /* --- UTILITIES --- */
async function buildQueryAndExecute(q: string, schemas: Record<string, any>): Promise<void> {
  console.log(`\r\n[❓] Asking: ${q}`);

  const SQLQuestion = `
  What would be the best SQL query to answer the following question:

  --- 
  ${q}
  ---

  The database schema is:
  ${JSON.stringify(schemas, null, 2)}
  `;

  const sql_statement = await OpenAIClient.chat.completions.create({
    model: "gpt-4o",
    messages: [
      {
        role: "system",
        content: SYSTEM_PROMPT,
      },
      {
        role: "user",
        content: SQLQuestion,
      }
    ]})

  const sql = sql_statement.choices[0].message.content?.trim();
  console.log(`[📝] SQL statement: ${sql}`);

  const response = await ArcadeClient.tools.execute({
    tool_name: "Sql.ExecuteQuery",
    user_id: USER_ID,
    input: {
      schema_name: SCHEMA_NAME,
      query: sql,
    },
  });

  console.log(response.output?.value);
}