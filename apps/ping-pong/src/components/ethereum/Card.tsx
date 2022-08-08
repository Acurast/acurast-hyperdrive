import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, TextField, DialogActions } from '@mui/material';
import * as IbcfSdk from '@ibcf/sdk';

import abi from './abi';
import EthereumSDK from 'src/services/ethereum';
import Button from 'src/components/base/Button';
import EthereumIcon from 'src/components/base/icons/ethereum';
import useAppContext from 'src/hooks/useAppContext';
import ValidatedBlocksTable from './Table';
import Constants from 'src/constants';
import Dialog from '../base/Dialog';
import CodeBlock from '../base/CodeBlock';

const Ethereum = () => {
    const { tezos, ethereum } = useAppContext();
    const [proof, setProof] = React.useState<IbcfSdk.EthereumProof>();
    const [pingProof, setPingProof] = React.useState<IbcfSdk.TezosProof>();
    const [operationHash, setOperationHash] = React.useState('');
    const [error, setError] = React.useState<Error>();
    const [confirmPingOpen, setConfirmPingOpen] = React.useState(false);

    const pong = React.useCallback(() => {
        const contract = new EthereumSDK.eth.Contract(abi, Constants.ethereum_client);
        EthereumSDK.eth
            .getAccounts()
            .then(async (accounts) => {
                return contract.methods
                    .pong()
                    .send({ from: accounts[0] })
                    .on('transactionHash', function (hash: string) {
                        setOperationHash(hash);
                    });
            })
            .then(console.log)
            .catch(setError);
    }, []);

    const handlePingProof = React.useCallback((e: any) => {
        try {
            setPingProof(JSON.parse(e.target.value));
        } catch (e) {
            setPingProof(undefined);
            // ignore
        }
    }, []);

    const confirmPing = React.useCallback(async () => {
        if (pingProof) {
            const contract = new EthereumSDK.eth.Contract(abi, Constants.ethereum_client);
            EthereumSDK.eth
                .getAccounts()
                .then(async (accounts) => {
                    const method = contract.methods.confirm_ping(
                        pingProof.level,
                        pingProof.merkle_root,
                        pingProof.key,
                        pingProof.value,
                        pingProof.proof,
                        [accounts[0]],
                        pingProof.signatures,
                    );
                    return method.send({ from: accounts[0] }).on('transactionHash', function (hash: string) {
                        setOperationHash(hash);
                    });
                })
                .then(console.log)
                .catch(setError);
        }
    }, [pingProof]);

    const generateProof = React.useCallback(async (block_number: number) => {
        const proof = await IbcfSdk.generateEthereumProof(
            EthereumSDK.eth,
            Constants.ethereum_client,
            '0',
            block_number,
        );
        setProof(proof);
    }, []);

    return (
        <>
            <Card variant="outlined">
                <CardContent>
                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Ethereum
                            </Typography>
                        </Grid>
                        <Grid item>
                            <EthereumIcon />
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Card variant="outlined">
                        <CardContent>
                            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                <Grid item>
                                    <Typography color="text.secondary" gutterBottom>
                                        Client
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Grid
                                        container
                                        direction="row"
                                        justifyContent="flex-end"
                                        alignItems="center"
                                        spacing={2}
                                    >
                                        <Grid item>
                                            <Button fullWidth size="small" onClick={() => setConfirmPingOpen(true)}>
                                                Confirm ping
                                            </Button>
                                        </Grid>
                                        <Grid item>
                                            <Button fullWidth size="small" onClick={pong}>
                                                Send Pong
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Grid container direction="row" justifyContent="center" alignItems="center">
                                <Grid item>Counter: {ethereum.clientStorage?.counter || 'No data'}</Grid>
                            </Grid>
                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Card variant="outlined">
                                <CardContent>
                                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                        <Grid item>
                                            <Typography color="text.secondary" gutterBottom>
                                                Blocks
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <ValidatedBlocksTable
                                                submissions={tezos.validatorStorage || []}
                                                generateProof={generateProof}
                                            />
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </CardContent>
                    </Card>
                </CardContent>
            </Card>

            <Dialog
                title="Confirm Ping (Insert proof below)"
                open={confirmPingOpen}
                onClose={() => {
                    setConfirmPingOpen(false);
                    setPingProof(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={confirmPing}>
                            Confirm ping
                        </Button>
                    </DialogActions>
                }
            >
                <TextField
                    error={!pingProof}
                    onChange={handlePingProof}
                    fullWidth
                    rows={10}
                    sx={{ height: 300 }}
                    multiline
                />
            </Dialog>

            <Dialog title="Error" open={!!error} onClose={() => setError(undefined)}>
                {error?.message || ''}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                <a
                    style={{ color: 'white' }}
                    target="_blank"
                    href={`https://goerli.etherscan.io/tx/${operationHash}`}
                    rel="noreferrer"
                >
                    Etherscan
                </a>
            </Dialog>
            <Dialog title="Proof" open={!!proof} onClose={() => setProof(undefined)}>
                {!!proof ? <CodeBlock language="json" code={JSON.stringify(proof, null, 2)} /> : ''}
            </Dialog>
        </>
    );
};

export default Ethereum;
