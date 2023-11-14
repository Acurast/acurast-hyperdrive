import { createContext } from 'react';

export interface IWalletContext {
    address?: string;
    connecting: boolean;
    connectAeternityWallet: () => Promise<void>;
}

const contextStub = {
    connecting: false,
    connectAeternityWallet: async () => {
        // stub
    },
};

const WalletContext = createContext<IWalletContext>(contextStub);

export default WalletContext;
