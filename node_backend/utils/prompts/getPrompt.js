export const getPrompt = (conversationContext, userMessage, resumeContent) => {
  return `
    ${conversationContext}
    Resume Data: ${resumeContent}
    User Input: ${userMessage}
  `;
};
