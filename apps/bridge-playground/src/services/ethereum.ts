import { ethers, Contract } from 'ethers';
import Logger from './logger';

let Ethereum: ethers.providers.Web3Provider;
try {
    Ethereum = new ethers.providers.Web3Provider((window as any).ethereum);
    (window as any).ethereum.request({ method: 'eth_requestAccounts' });
} catch {
    Logger.error('No web3 wallet found.');
}

export { Contract };

export default Ethereum!;
