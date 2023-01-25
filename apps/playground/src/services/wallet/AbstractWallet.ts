import { TezosToolkit } from '@taquito/taquito';
import Constants from 'src/constants';
import Tezos from '../tezos';
import { Signer } from './Signer';

abstract class AbstractWallet {
    protected source;
    protected rpc = Constants.rpc;
    protected pkh?: string;
    protected tezos: TezosToolkit;

    constructor(source: string, public signer: Signer) {
        this.tezos = Tezos;
        this.source = source;
    }

    /**
     * @description Set RPC address.
     *
     * @returns {void}
     */
    public setRPC(rpc: string): void {
        this.rpc = rpc;
    }

    /**
     * @description Retrieve the Public Key Hash of the account that is currently in use by the wallet.
     *
     * @param options Options to use while fetching the PKH.
     *
     * @returns A Public Key Hash string.
     */
    public getPkh() {
        return this.signer.publicKeyHash();
    }

    /**
     * @description Return the public key of the account used by the signer
     */
    public publicKey = () => {
        return this.signer.publicKey();
    };

    /**
     * @description Optionally return the secret key of the account used by the signer
     */
    public secretKey = () => {
        return this.signer.secretKey();
    };
}

export default AbstractWallet;
