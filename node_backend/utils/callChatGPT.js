import OpenAI from 'openai';
import getSecrets from "./getSecrets.js";
import { getBotInstructions } from './prompts/getBotInstructions.js';

export const callChatGPT = async (prompt) => {
  try {
    const secrets = await getSecrets();
    const openai = new OpenAI({ apiKey: secrets.OPENAI_API_KEY });
    const messages = [
      { role: "system", content: getBotInstructions() },
      { role: "user", content: prompt },
    ];
    
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: messages,
    });
    return response.choices[0].message.content;
  } catch (error) {
    console.error("Error in callChatGPT:", error);
    return "";
  }
};
