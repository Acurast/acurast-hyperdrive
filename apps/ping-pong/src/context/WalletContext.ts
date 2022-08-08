import { createContext } from 'react';

export interface IWalletContext {
    pkh?: string;
    publicKey?: string;
    connecting: boolean;
    connectTezosWallet: () => Promise<void>;
}

const contextStub = {
    connecting: false,
    connectTezosWallet: async () => {
        // stub
    },
};

const WalletContext = createContext<IWalletContext>(contextStub);

export default WalletContext;
