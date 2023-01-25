import { TezosToolkit } from '@taquito/taquito';
import Constants from 'src/constants';

const Tezos = new TezosToolkit(Constants.rpc);

export default Tezos;
