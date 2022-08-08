import Web3 from 'web3';

class Ethereum {
    private web3: Web3 = new Web3(Web3.givenProvider);

    constructor() {
        this.web3 = new Web3(Web3.givenProvider);

        this.web3.eth.requestAccounts().then(console.log);
    }
}

export default Ethereum;
