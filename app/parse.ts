import Arcade from "@arcadeai/arcadejs";

const ARCADE_API_KEY = Bun.env.ARCADE_API_KEY;
const ARCADE_URL = Bun.env.ARCADE_URL;
const USER_ID = Bun.env.USER_ID;
const DB_DIALECT = "POSTGRES"; // change if needed

const SYSTEM_PROMPT = `
You are a document managment expert.  
You are given a document and a question about the document.  
You will use the tools provided to you to answer the question.  
You use no prior knowledge.
`;

const client = new Arcade({
  baseURL: ARCADE_URL,
  apiKey: ARCADE_API_KEY,
});

const parseTools = await client.tools.formatted.list({
  format: "openai",
  toolkit: "parse",
});

console.log("⚙️ Found the following tools:");
parseTools.items.forEach((tool) => {
  // @ts-ignore
  console.log(`${tool.function.name}: ${tool.function.description}`);
});

const text = await chat(
`Can you parse the document located at https://www.adobe.com/be_en/active-use/pdf/Alice_in_Wonderland.pdf`,
);

console.log(text);

/* --- UTILITIES --- */

function buildPrompt(question: string) {
  return {
    messages: [
      {
        role: "system",
        content: SYSTEM_PROMPT,
      },
      {
        role: "user",
        content: question,
      },
    ],
    model: "gpt-4o",
    user: USER_ID,
    tools: ["Parse.ParseDocument","Parse.ExtractMetadata","Parse.Summarize"],
    tool_choice: "generate",
  };
}

async function chat(
  question: string,
  replace: string = "..."
): Promise<string | undefined> {
  console.log(`\r\n[❓] Asking: ${question.replace(replace, " {...}")}\r\n`);
  const response = await client.chat.completions.create(buildPrompt(question));
  displayResponse(response);
  return response.choices?.[0]?.message?.content;
}

function displayResponse(response: Arcade.Chat.ChatResponse) {
  console.log("--- response ---");
  console.log(response.choices?.[0]?.message?.content);
  console.log("\r\n--- tool calls ---");
  response.choices?.[0]?.message?.tool_calls?.map((tool) => {
    if (!tool || !tool.function) return;
    console.log(`${tool.function.name}: ${tool.function.arguments}`);
  });
  console.log("---");
}
