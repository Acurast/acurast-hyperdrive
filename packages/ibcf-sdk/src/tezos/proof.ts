import { ContractAbstraction } from '@taquito/taquito';
import { MichelsonType, pack } from './utils';

export interface TezosProof {
    level: number;
    merkle_root: string;
    key: string;
    value: string;
    proof: [string, string][];
    signatures: [string, string][];
}

export async function generateProof(
    contract: ContractAbstraction<any>,
    owner: string,
    key: string,
    blockLevel: number,
): Promise<TezosProof> {
    const proof = await contract.contractViews
        .get_proof({ key, owner, level: blockLevel })
        .executeView({ viewCaller: owner });

    const signers = [];
    const signatures: [string, string][] = [];
    for (const [k, { r, s }] of proof.signatures.entries()) {
        signers.push(pack(k, MichelsonType.address));
        signatures.push(['0x' + r, '0x' + s]);
    }

    const blindedPath = proof.proof.reduce(() => {
        // TODO
    }, []);

    console.log(proof);

    return {
        level: proof.level.toNumber(),
        merkle_root: '0x' + proof.merkle_root,
        key: '0x' + proof.key,
        value: '0x' + proof.value,
        proof: blindedPath,
        signatures,
    };
}
