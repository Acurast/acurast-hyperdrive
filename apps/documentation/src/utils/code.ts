import * as ts from "typescript";
import * as IbcfSdk from "ibcf-sdk";
import { TezosToolkit } from "@taquito/taquito";
import { ethers } from "ethers";

function replaceAll(string: string, search: string, replace: string) {
  return string.split(search).join(replace);
}

const removeImports = (code: string) => {
  return code
    .split("\n")
    .map((l) => {
      let include = true;

      if (l.trim().startsWith("import")) {
        include = false;
      }

      const out = include ? l : undefined;

      return out;
    })
    .filter((l) => !!l)
    .join("\n");
};

export const runCode = (rawCode: string, setOutput: (str: string) => void) => {
  let code = rawCode;

  const coinlib = {};
  let output = "";
  const appendOutput = (str: string) => {
    output += "\n" + str;
    setOutput(output.trim());
  };

  const myLog = (...args: any[]) => {
    console.log("CODE_RUNNER:", ...args);
    appendOutput(
      args
        .map((arg) =>
          typeof arg === "object" ? JSON.stringify(arg, null, 2) : arg
        )
        .join(" ")
    );
  };

  const lib = {
    IbcfSdk: IbcfSdk,
    Ethereum: IbcfSdk.Ethereum,
    Tezos: IbcfSdk.Tezos,
    TezosToolkit: TezosToolkit,
    ethers: ethers,
  };

  code = replaceAll(code, "console.log", "progress");
  code = removeImports(code);
  code = ts.transpile(`({
        run: async (prelude: any, progress: any): string => {
          Object.keys(prelude).forEach(key => {
            window[key] = prelude[key]
          })
          return (async () => {
            ${code};
            if (typeof result !== 'undefined') {
              return result
            }
          })()
        })`);
  let runnable: any;
  return new Promise((resolve) => {
    try {
      runnable = eval(code);
      runnable
        .run(lib, myLog)
        .then((result: string) => {
          if (result) {
            appendOutput("Returned:\n" + JSON.stringify(result, null, 2));
          }
          resolve(result);
        })
        .catch((err: any) => {
          console.warn(err);
          appendOutput(JSON.stringify(err, null, 2));
          resolve(err);
        });
    } catch (e) {
      appendOutput(e);
      console.error(e);
      resolve(e);
    }
  });
};
