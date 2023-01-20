import * as ts from "typescript";
import * as IbcfSdk from "ibcf-sdk";
import { TezosToolkit } from "@taquito/taquito";
import { ethers } from "ethers";

const tezosSdk = new TezosToolkit("https://rpc.ghostnet.teztnets.xyz");
const stateAggregator = new IbcfSdk.Tezos.Contracts.StateAggregator.Contract(
  tezosSdk,
  "KT1Aqdz8opKsfADxmF2vf6NMoYwgamL5R4KT"
);

const ETHEREUM_RPC =
  "https://goerli.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f";
const provider = new ethers.providers.JsonRpcProvider(ETHEREUM_RPC);

const proofGenerator = new IbcfSdk.Ethereum.ProofGenerator(provider);

const destinationRegistryIndex = "05".padStart(64, "0");
const amountRegistryIndex = "06".padStart(64, "0");
const destinationSlot = ethers.utils.keccak256(
  "0x" + "01" + destinationRegistryIndex
);
const amountSlot = ethers.utils.keccak256("0x" + "01" + amountRegistryIndex);

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

  console.log(code);
  code = replaceAll(code, "console.log", "progress");
  code = removeImports(code);
  console.log(code);
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
  console.log(code);
  // console.log("TRANSPILED code", code);
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
