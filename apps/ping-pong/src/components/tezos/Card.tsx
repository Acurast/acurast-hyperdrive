import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, DialogActions } from '@mui/material';
import * as IbcfSdk from '@ibcf/sdk';
import TezosSdk from 'src/services/tezos';
import Button from 'src/components/base/Button';
import TezosIcon from 'src/components/base/icons/tezos';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Dialog from '../base/Dialog';
import ValidatedBlocksTable from './Table';
import CodeBlock from '../base/CodeBlock';
import TextField from '../base/TextField';

const Tezos = () => {
    const { tezos } = useAppContext();
    const [error, setError] = React.useState('');
    const [sending, setSending] = React.useState(false);
    const [proof, setProof] = React.useState<IbcfSdk.TezosProof>();
    const [pongProof, setPongProof] = React.useState<IbcfSdk.EthereumProof>();
    const [operationHash, setOperationHash] = React.useState('');
    const [confirmPongOpen, setConfirmPongOpen] = React.useState(false);

    const ping = React.useCallback(async () => {
        // 1. Call ping entrypoint
        setSending(true);
        try {
            const contract = await TezosSdk.contract.at(Constants.tezos_client);
            const operation = await contract.methods.ping().send();
            setOperationHash(operation.hash);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setSending(false);
        }
    }, []);

    const generateProof = React.useCallback(async (blockLevel: number) => {
        const contract = await TezosSdk.contract.at(Constants.tezos_state);
        const proof = await IbcfSdk.generateTezosProof(
            contract,
            Constants.tezos_client,
            IbcfSdk.Utils.utf8ToHex('counter'),
            blockLevel,
        );
        setProof(proof);
    }, []);

    const handlePongProof = React.useCallback((e: any) => {
        try {
            setPongProof(JSON.parse(e.target.value));
        } catch (e) {
            setPongProof(undefined);
            // ignore
        }
    }, []);

    const confirmPong = React.useCallback(async () => {
        setSending(true);
        if (pongProof) {
            const contract = await TezosSdk.contract.at(Constants.tezos_client);
            const operation = await contract.methods
                .confirm_pong(pongProof.account_proof_rlp, pongProof.block_number, pongProof.storage_proof_rlp)
                .send();
            setOperationHash(operation.hash);
        }
        setSending(false);
    }, [pongProof]);

    return (
        <>
            <Card variant="outlined">
                <CardContent>
                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Tezos
                            </Typography>
                        </Grid>
                        <Grid item>
                            <TezosIcon />
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
                                            <Button fullWidth size="small" onClick={ping}>
                                                Send Ping
                                            </Button>
                                        </Grid>
                                        <Grid item>
                                            <Button fullWidth size="small" onClick={() => setConfirmPongOpen(true)}>
                                                Confirm Pong
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Grid container direction="row" justifyContent="center" alignItems="center">
                                <Grid item>Counter: {tezos.clientStorage?.counter.toNumber() || 'No data'}</Grid>
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
                                                blocks={tezos.stateAggregatorStorage?.blocks || []}
                                                generateProof={generateProof}
                                            />
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </CardContent>
                    </Card>
                </CardContent>
                <CardActions>
                    <Grid container direction="row" justifyContent="center" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                {sending ? 'Sending...' : ''}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardActions>
            </Card>

            <Dialog
                title="Confirm Pong (Insert proof below)"
                open={confirmPongOpen}
                onClose={() => {
                    setConfirmPongOpen(false);
                    setPongProof(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={confirmPong}>
                            Confirm pong
                        </Button>
                    </DialogActions>
                }
            >
                <TextField
                    error={!pongProof}
                    onChange={handlePongProof}
                    fullWidth
                    rows={10}
                    sx={{ height: 300 }}
                    multiline
                />
            </Dialog>

            <Dialog title="Error" open={!!error} onClose={() => setError('')}>
                {error}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                <a
                    style={{ color: 'white' }}
                    target="_blank"
                    href={`https://ghostnet.tzkt.io/${operationHash}`}
                    rel="noreferrer"
                >
                    TzKT
                </a>
            </Dialog>
            <Dialog title="Proof" open={!!proof} onClose={() => setProof(undefined)}>
                {!!proof ? <CodeBlock language="json" code={JSON.stringify(proof, null, 2)} /> : ''}
            </Dialog>
        </>
    );
};

export default Tezos;
