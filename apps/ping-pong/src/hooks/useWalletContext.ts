import { useContext } from 'react';

import WalletContext, { IWalletContext } from '../context/WalletContext';

function useWalletContext(): IWalletContext {
    const context = useContext<IWalletContext>(WalletContext);
    if (context == null) {
        throw new Error('`useWalletContext` not available.');
    }
    return context;
}

export default useWalletContext;
