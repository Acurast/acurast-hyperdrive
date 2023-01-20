module.exports = {
    extends: ['../../.eslintrc.json'],
    root: false,
    parser: '@typescript-eslint/parser', // Specifies the ESLint parser
    parserOptions: {
        ecmaVersion: 2020, // Allows for the parsing of modern ECMAScript features
        sourceType: 'module', // Allows for the use of imports
    },
    extends: ['plugin:@typescript-eslint/recommended', 'plugin:prettier/recommended'],
    ignorePatterns: ['dist/**', 'node_modules/**', 'api_documentation/**'],
};
