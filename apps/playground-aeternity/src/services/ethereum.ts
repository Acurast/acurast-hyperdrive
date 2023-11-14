import { ethers, Contract } from 'ethers';
import Constants from 'src/constants';
import { Network } from 'src/context/AppContext';
import Logger from './logger';

let Ethereum: ethers.providers.Web3Provider;
try {
    Ethereum = new ethers.providers.Web3Provider((window as any).ethereum);
    (window as any).ethereum.request({ method: 'eth_requestAccounts' });
    // (window as any).ethereum.request({
    //     method: 'wallet_addEthereumChain',
    //     params: [
    //         {
    //             chainId: Constants[Network.Avalanche].ethChainId,
    //             chainName: 'avalanche-fuji',
    //             rpcUrls: ['https://avalanche-fuji.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f'],
    //         },
    //     ],
    // });
    (window as any).ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: Constants[Network.Ethereum].ethChainId }],
    });
} catch {
    Logger.error('No web3 wallet found.');
}

export { Contract };

export default Ethereum!;
