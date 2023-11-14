import React from 'react';
import Aeternity, { connect } from 'src/services/aeternity';
import Logger from '../services/logger';
import WalletContext from './WalletContext';

const WalletProvider: React.FC<{ children: React.ReactNode }> = (props) => {
    const [connecting, setConnecting] = React.useState(true);
    const [account, setAccount] = React.useState<string>();

    React.useEffect(() => {
        // WalletService.Tezos.getActiveAccount()
        //     .then((account) => {
        //         setAccount(account);
        //     })
        //     .finally(() => setConnecting(false));
    }, []);

    const connectAeternityWallet = React.useCallback(async () => {
        try {
            setConnecting(true);
            await connect();
            setAccount(Aeternity.address);
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
                address: account,
                connectAeternityWallet,
            }}
        >
            {props.children}
        </WalletContext.Provider>
    );
};

export default WalletProvider;
