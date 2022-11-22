import {
    NetworkType,
    PermissionScope,
    DAppClient,
    DAppClientOptions,
    AccountInfo,
    ColorMode,
} from '@airgap/beacon-sdk';
import { TransactionOperationParameter } from '@taquito/rpc';
import type { BatchOperation, ParamsWithKind, TransactionOperation } from '@taquito/taquito';

import AbstractWallet from './AbstractWallet';
import BeaconSigner from './BeaconSigner';

class Beacon extends AbstractWallet {
    private client: DAppClient;

    constructor() {
        const options: DAppClientOptions = {
            colorMode: ColorMode.DARK,
            preferredNetwork: NetworkType.CUSTOM,
            name: 'PingPong',
        };
        super('BEACON', new BeaconSigner(new DAppClient(options)));
        this.client = this.signer.client;

        this.tezos.setProvider({ signer: this.signer });
    }

    public async transfer(
        address: string,
        parameter: TransactionOperationParameter,
        amount = 0,
    ): Promise<TransactionOperation> {
        return this.tezos.contract.transfer({
            to: address,
            amount,
            parameter,
        });
    }

    public async transferBatch(ops: ParamsWithKind[]): Promise<BatchOperation> {
        return this.tezos.contract.batch(ops).send();
    }

    /**
     * @description Retrieve active account.
     *
     * @returns {Promise<AccountInfo | undefined>} A promise that resolves to {AccountInfo}.
     */
    public async getActiveAccount(): Promise<AccountInfo | undefined> {
        return this.client.getActiveAccount();
    }

    /**
     * @description Connect to the wallet.
     *
     * @param options Options passed to the wallet.
     *
     * @returns A promise that resolves to void;
     */
    public connect = async (network: { name: string; rpc: string }): Promise<void> => {
        let networkType = NetworkType.CUSTOM;
        if (Object.values<string>(NetworkType).includes(network.name)) {
            networkType = network.name as NetworkType;
        }

        const permissionsOutput = await this.client.requestPermissions({
            network: { type: networkType, rpcUrl: network.rpc },
            scopes: [PermissionScope.SIGN, PermissionScope.OPERATION_REQUEST],
        });

        this.rpc = network.rpc;
        this.pkh = permissionsOutput.address;
    };
}

export default Beacon;
