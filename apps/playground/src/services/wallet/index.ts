import Beacon from './Beacon';

const WalletService = {
    Tezos: new Beacon(),
};

export default WalletService;

(window as any).WalletService = WalletService;
