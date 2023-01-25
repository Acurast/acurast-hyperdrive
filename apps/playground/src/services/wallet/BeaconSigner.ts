import { DAppClient, SigningType } from '@airgap/beacon-sdk';
import bs58check from 'bs58check';

import { Signer } from './Signer';

class BeaconSigner implements Signer {
    public client;

    constructor(client: DAppClient) {
        this.client = client;
    }

    public sign = async (
        bytes: string,
        magicByte?: Uint8Array,
        signingType = SigningType.OPERATION,
    ): Promise<{
        bytes: string;
        sig: string;
        prefixSig: string;
        sbytes: string;
    }> => {
        const result = await this.client.requestSignPayload({
            signingType,
            payload: (signingType === SigningType.OPERATION ? '03' : '') + bytes, // 0x03 generic prefix
        });

        let sbytes: Buffer | string = bs58check.decode(result.signature);
        if (result.signature.startsWith('edsig') || result.signature.startsWith('spsig1')) {
            sbytes = sbytes.slice(5).toString('hex');
        } else if (result.signature.startsWith('p2sig')) {
            sbytes = sbytes.slice(4).toString('hex');
        } else {
            sbytes = sbytes.slice(3).toString('hex');
        }

        return {
            bytes,
            sig: sbytes,
            prefixSig: result.signature,
            sbytes: `${bytes}${sbytes}`,
        };
    };

    public publicKey = async (): Promise<string> => {
        const pk = (await this.client.getActiveAccount())?.publicKey;
        if (!pk) {
            throw new Error('Could not retreive public key.');
        }
        return pk;
    };

    public publicKeyHash = async (): Promise<string> => {
        const pkh = (await this.client.getActiveAccount())?.address;
        if (!pkh) {
            throw new Error('Could not retreive public key hash.');
        }
        return pkh;
    };

    secretKey(): Promise<string | undefined> {
        throw new Error('Method not implemented.');
    }

    public isReady = async (): Promise<void> => await this.client.ready;
}

export default BeaconSigner;
