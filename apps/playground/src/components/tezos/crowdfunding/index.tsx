import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, DialogActions } from '@mui/material';

import TezosSdk from 'src/services/tezos';
import Button from 'src/components/base/Button';
import TezosIcon from 'src/components/base/icons/tezos';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Dialog from '../../base/Dialog';
import WrapsTable from './Table';
import TextField from '../../base/TextField';
import useWalletContext from 'src/hooks/useWalletContext';
import Logger from 'src/services/logger';
import ValidatorCard from '../ValidatorCard';

const TezosCrowdfunding = () => {
    const { tezos, network } = useAppContext();
    const { connectTezosWallet } = useWalletContext();
    const [error, setError] = React.useState('');
    const [confirming, setConfirming] = React.useState(false);
    const [proof, setProof] = React.useState<any>();
    const [operationHash, setOperationHash] = React.useState('');
    const [confirmPongModalOpen, setConfirmPongModalOpen] = React.useState(false);

    const confirmFunding = React.useCallback(async () => {
        try {
            const crowdfunding = await TezosSdk.contract.at(Constants[network].tezos_crowdfunding);

            const result = await crowdfunding.methods
                .funding_from_eth(
                    proof.account_proof_rlp,
                    proof.amount_proof_rlp,
                    proof.block_number,
                    proof.funder_proof_rlp,
                    proof.nonce,
                )
                .send();

            setConfirming(true);
            setOperationHash(result.hash);
            await result.confirmation(1);
        } catch (e: any) {
            Logger.error(e);
            return setError(e.message);
        } finally {
            setConfirming(false);
        }
    }, [proof]);

    const handleProof = React.useCallback((e: any) => {
        try {
            setProof(JSON.parse(e.target.value));
        } catch (e) {
            setProof(undefined);
            // ignore
        }
    }, []);

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
                    <ValidatorCard />
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Card variant="outlined">
                        <CardContent>
                            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                <Grid item>
                                    <Typography color="text.secondary" gutterBottom>
                                        Crowdfunding
                                    </Typography>
                                    <Typography variant="caption" fontSize={10}>
                                        <a
                                            target="_blank"
                                            style={{ color: 'white' }}
                                            href={`${Constants[network].tzkt}/${Constants[network].tezos_crowdfunding}`}
                                            rel="noreferrer"
                                        >
                                            {Constants[network].tezos_crowdfunding}
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
                                            <Button
                                                fullWidth
                                                size="small"
                                                onClick={() => setConfirmPongModalOpen(true)}
                                            >
                                                Submit Proof
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
                                                Ethereum Funding
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <WrapsTable fundings={tezos.crowdfundInfo?.eth_funding || []} />
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>

                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Card variant="outlined">
                                <CardContent>
                                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                        <Grid item>
                                            <Typography color="text.secondary" gutterBottom>
                                                Tezos Funding
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <WrapsTable fundings={tezos.crowdfundInfo?.tezos_funding || []} />
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
                                {confirming ? 'Confirming...' : ''}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardActions>
            </Card>

            <Dialog
                title="Confirm funding (Insert proof below)"
                open={confirmPongModalOpen}
                onClose={() => {
                    setConfirmPongModalOpen(false);
                    setProof(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={confirmFunding}>
                            Confirm Funding
                        </Button>
                    </DialogActions>
                }
            >
                <TextField error={!proof} onChange={handleProof} fullWidth rows={10} sx={{ height: 300 }} multiline />
            </Dialog>

            <Dialog title="Error" open={!!error} onClose={() => setError('')}>
                {error}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                <a
                    style={{ color: 'white' }}
                    target="_blank"
                    href={`${Constants[network].tzkt}/${operationHash}`}
                    rel="noreferrer"
                >
                    TzKT
                </a>
            </Dialog>
        </>
    );
};

export default TezosCrowdfunding;
