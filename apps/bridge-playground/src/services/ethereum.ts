import { ethers, Contract } from 'ethers';

const Ethereum = new ethers.providers.Web3Provider((window as any).ethereum);

export { Contract };

export default Ethereum;
