/**
 * @description Copy text to clipboard
 *
 * @param {string} text
 */
export const copyToClipboard = (text: string): void => {
    navigator.clipboard.writeText(text);
};
