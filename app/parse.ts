import Arcade from "@arcadeai/arcadejs";

const ARCADE_API_KEY = Bun.env.ARCADE_API_KEY;
const ARCADE_URL = Bun.env.ARCADE_URL;
const USER_ID = Bun.env.USER_ID;

const SYSTEM_PROMPT = `
You are a document managment expert.  
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

const {tool_content: text} = await chat(
`Get the markdown content from the document located at "https://www.adobe.com/be_en/active-use/pdf/Alice_in_Wonderland.pdf"?`,
);

console.log("--- text ---");    
console.log(text?.slice(0, 5000) + '...');
console.log("---");    



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
    tools: ["Parse.ParseDocument"],
    tool_choice: "generate",
  };
}

async function chat(
  question: string,
  replace: string = "..."
): Promise<{content: string | undefined, tool_content:string | undefined}> {
  console.log(`\r\n[❓] Asking: ${question.replace(replace, " {...}")}\r\n`);
  const response = await client.chat.completions.create(buildPrompt(question));
  displayResponse(response);
  return {
    content: response.choices?.[0]?.message?.content, 
    tool_content: response.choices?.[0]?.tool_messages?.filter(m => m.role === "tool").map((tool) => tool.content)[0]
  }
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
