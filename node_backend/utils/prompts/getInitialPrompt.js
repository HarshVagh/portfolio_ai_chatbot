export const getInitialPrompt = (resumeText, additionalDescription) => {
  return `
    Resume Data: ${resumeText}
    User Input: ${additionalDescription}
  `;
};