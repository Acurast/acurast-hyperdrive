// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion
const path = require("path");

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

const organizationName = "airgap-it";
const projectName = "ibcf";

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "IBCF Documentation",
  tagline: "Inter Blockchain Communication Framework",
  url: "https://github.com",
  baseUrl: process.env.NODE_ENV === "development" ? "/" : `/${projectName}/`,
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName,
  projectName, // Usually your repo name.

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: "https://github.com/airgap-it/ibcf-docs",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: "Documentation",
        items: [
          {
            href: `https://${organizationName}.github.io/${projectName}/api`,
            label: "API Documentation (TypeDoc)",
            position: "right",
          },
          {
            href: "https://github.com/facebook/docusaurus",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} Papers AG.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ["solidity"],
      },
    }),
  plugins: [
    path.join(__dirname, "/plugins/monaco-editor"),
    path.join(__dirname, "/plugins/webpack"),
  ],
};

module.exports = config;
