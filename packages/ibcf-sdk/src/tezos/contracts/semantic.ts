import BigNumber from 'bignumber.js';
import type { MichelsonV1Expression } from '@taquito/rpc';
import { BigMapAbstraction, ContractProvider } from '@taquito/taquito';
import { Schema, Semantic } from '@taquito/michelson-encoder';

// Override the default michelson encoder semantic to provide richer abstraction over storage properties
export const smartContractAbstractionSemantic: (p: ContractProvider) => Semantic = (provider: ContractProvider) => ({
    // Provide a specific abstraction for BigMaps
    big_map: (val: MichelsonV1Expression, code: MichelsonV1Expression) => {
        if (!val || !('int' in val) || val.int === undefined) {
            // Return an empty object in case of missing big map ID
            return {};
        } else {
            const schema: any = new Schema(code);
            return new BigMapAbstraction(new BigNumber(val.int) as any, schema, provider);
        }
    },
});
