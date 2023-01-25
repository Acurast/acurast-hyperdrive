/**
 * @description Signer interface
 */
export interface Signer {
    client: any;
    /**
     * @description Sign operations
     *
     * @param op Operation to sign
     * @param magicByte Magic bytes 1 for block, 2 for endorsement, 3 for generic
     */
    sign(
        op: any,
        magicByte?: Uint8Array,
        type?: SigningType,
    ): Promise<{
        bytes: string;
        sig: string;
        prefixSig: string;
        sbytes: string;
    }>;

    /**
     * @description Return the public key of the account used by the signer
     */
    publicKey(): Promise<string>;

    /**
     * @description Return the public key hash of the account used by the signer
     */
    publicKeyHash(): Promise<string>;

    /**
     * @description Optionally return the secret key of the account used by the signer
     */
    secretKey(): Promise<string | undefined>;

    /**
     *  @description Waits for the ledger to be ready or timeouts after 3 seconds
     */
    isReady(): Primise<void>;
}
