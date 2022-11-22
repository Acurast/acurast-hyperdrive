import Beacon from './Beacon';
import Ethereum from './Ethereum';

const WalletService = {
    Tezos: new Beacon(),
    Ethereum: new Ethereum(),
};

export default WalletService;

(window as any).WalletService = WalletService;
