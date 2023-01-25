import { AccountInfo } from '@airgap/beacon-sdk';
import React from 'react';
import Constants from 'src/constants';
import Logger from '../services/logger';
import WalletService from '../services/wallet';
import WalletContext from './WalletContext';

const WalletProvider: React.FC<{ children: React.ReactNode }> = (props) => {
    const [connecting, setConnecting] = React.useState(true);
    const [account, setAccount] = React.useState<AccountInfo>();

    React.useEffect(() => {
        WalletService.Tezos.getActiveAccount()
            .then((account) => {
                setAccount(account);
            })
            .finally(() => setConnecting(false));
    }, []);

    const connectTezosWallet = React.useCallback(async () => {
        try {
            setConnecting(true);
            await WalletService.Tezos.connect({
                name: Constants.network,
                rpc: Constants.rpc,
            });
            const account = await WalletService.Tezos.getActiveAccount();
            setAccount(account);
        } catch (e) {
            Logger.error(e);
        } finally {
            setConnecting(false);
        }
    }, []);

    return (
        <WalletContext.Provider
            value={{
                connecting,
                pkh: account?.address,
                publicKey: account?.publicKey,
                connectTezosWallet,
            }}
        >
            {props.children}
        </WalletContext.Provider>
    );
};

export default WalletProvider;
