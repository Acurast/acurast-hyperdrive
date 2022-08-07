var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { MichelsonType, pack } from './utils';
export function generateTezosProof(contract, owner, key, blockLevel) {
    return __awaiter(this, void 0, void 0, function* () {
        const proof = yield contract.contractViews
            .get_proof({ key, owner, level: blockLevel })
            .executeView({ viewCaller: owner });
        const signers = [];
        const signatures = [];
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
    });
}
