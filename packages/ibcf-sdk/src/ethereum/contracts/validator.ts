import { Signer } from '@ethersproject/abstract-signer';
import { JsonRpcProvider, TransactionResponse } from '@ethersproject/providers';
import { Contract as EthersContract } from '@ethersproject/contracts';
import BigNumber from 'bignumber.js';
import ABI from './abi/validator.json';

export interface Snapshot {
    snapshot_number: number;
    merkle_root: string;
}

export class Contract {
    private signer: Signer;
    private provider: JsonRpcProvider;
    private contractAddress: string;

    constructor(signer: Signer, contractAddress: string) {
        this.signer = signer;
        this.provider = signer.provider as JsonRpcProvider;
        this.contractAddress = contractAddress;
    }

    async getCurrentSnapshot(): Promise<BigNumber> {
        const contract = new EthersContract(this.contractAddress, ABI, this.provider);

        return BigNumber((await contract.get_current_snapshot()).toString());
    }

    async getCurrentSnapshotSubmissions(): Promise<string[]> {
        const contract = new EthersContract(this.contractAddress, ABI, this.provider);

        return contract.get_current_snapshot_submissions();
    }

    async latestSnapshot(): Promise<Snapshot> {
        const contract = new EthersContract(this.contractAddress, ABI, this.provider);

        const history = await contract.get_history();

        const latestSnapshot = history[history.length - 1];
        const merkle_root = await contract.get_state_root(latestSnapshot);

        return {
            snapshot_number: latestSnapshot.toNumber(),
            merkle_root,
        };
    }

    async submitStateRoot(snapshot: BigNumber, state_root: string): Promise<TransactionResponse> {
        const contract = new EthersContract(this.contractAddress, ABI, this.signer);

        return contract.submit_state_root(snapshot.toString(), state_root);
    }
}
