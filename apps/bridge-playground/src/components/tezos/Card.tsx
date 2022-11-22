import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, DialogActions } from '@mui/material';
import * as IbcfSdk from '@ibcf/sdk';
import TezosSdk from 'src/services/tezos';
import Button from 'src/components/base/Button';
import TezosIcon from 'src/components/base/icons/tezos';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Dialog from '../base/Dialog';
import WrapsTable from './Table';
import CodeBlock from '../base/CodeBlock';
import TextField from '../base/TextField';
import useWalletContext from 'src/hooks/useWalletContext';
import AssetCard from './AssetCard';

const Tezos = () => {
    const { tezos } = useAppContext();
    const { connectTezosWallet } = useWalletContext();
    const [error, setError] = React.useState('');
    const [sending, setSending] = React.useState(false);
    const [proof, setProof] = React.useState<IbcfSdk.Tezos.Proof.TezosProof>();
    const [pongProof, setPongProof] = React.useState<IbcfSdk.EthereumProof>();
    const [operationHash, setOperationHash] = React.useState('');
    const [confirmPongOpen, setConfirmPongOpen] = React.useState(false);

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
            try {
                const contract = await TezosSdk.contract.at(Constants.tezos_bridge);
                const operation = await contract.methods
                    .confirm_pong(pongProof.account_proof_rlp, pongProof.block_number, pongProof.storage_proof_rlp)
                    .send();
                setOperationHash(operation.hash);
            } catch (e: any) {
                setError(e.message);
            } finally {
                setSending(false);
            }
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
                            <Button fullWidth size="small" onClick={connectTezosWallet}>
                                Connect
                            </Button>
                        </Grid>
                        <Grid item>
                            <TezosIcon />
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    {tezos.bridgeStorage ? <AssetCard asset={tezos.bridgeStorage?.asset} /> : null}
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Card variant="outlined">
                        <CardContent>
                            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                <Grid item>
                                    <Typography color="text.secondary" gutterBottom>
                                        Bridge
                                    </Typography>
                                    <Typography variant="caption" fontSize={10}>
                                        <a
                                            target="_blank"
                                            style={{ color: 'white' }}
                                            href={`${Constants.tzkt}/${Constants.tezos_bridge}`}
                                            rel="noreferrer"
                                        >
                                            {Constants.tezos_bridge}
                                        </a>
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
                                            <Button fullWidth size="small" onClick={() => setConfirmPongOpen(true)}>
                                                Unwrap
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Card variant="outlined">
                                <CardContent>
                                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                        <Grid item>
                                            <Typography color="text.secondary" gutterBottom>
                                                Unwraps
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <WrapsTable wraps={[]} />
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
                    href={`${Constants.tzkt}/${operationHash}`}
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
