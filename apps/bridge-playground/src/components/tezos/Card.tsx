import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, DialogActions } from '@mui/material';
import * as IbcfSdk from 'ibcf-sdk';
import TezosSdk from 'src/services/tezos';
import Button from 'src/components/base/Button';
import TezosIcon from 'src/components/base/icons/tezos';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Dialog from '../base/Dialog';
import WrapsTable from './Table';
import TextField from '../base/TextField';
import useWalletContext from 'src/hooks/useWalletContext';
import AssetCard from './AssetCard';
import Logger from 'src/services/logger';
import ValidatorCard from './ValidatorCard';

const Tezos = () => {
    const { tezos } = useAppContext();
    const { connectTezosWallet, pkh } = useWalletContext();
    const [error, setError] = React.useState('');
    const [operationHash, setOperationHash] = React.useState('');
    const [wrapModalOpen, setUnwrapModalOpen] = React.useState(false);
    const [destination, setDestination] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();
    const [confirming, setConfirming] = React.useState(false);

    const unwrap = React.useCallback(async () => {
        if (!destination || destination.length < 32) {
            return setError('Invalid destination!');
        }
        if (!amount || amount == '0') {
            return setError('Invalid amount!');
        }

        try {
            const bridge = new IbcfSdk.Tezos.Contracts.Bridge.Contract(TezosSdk, Constants.tezos_bridge);
            const storage = await bridge.getStorage();
            const asset = await TezosSdk.contract.at(storage.asset_address);

            const add_operator = await asset.methods.update_operators([
                {
                    add_operator: {
                        owner: pkh,
                        operator: Constants.tezos_bridge,
                        token_id: 0,
                    },
                },
            ]);
            const remove_operator = await asset.methods.update_operators([
                {
                    remove_operator: {
                        owner: pkh,
                        operator: Constants.tezos_bridge,
                        token_id: 0,
                    },
                },
            ]);

            const unwrap = await bridge.unwrap({
                destination,
                amount,
            });

            const result = await TezosSdk.contract
                .batch()
                .withContractCall(add_operator)
                .withContractCall(unwrap)
                .withContractCall(remove_operator)
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
    }, [destination, amount]);

    const handleDestination = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setDestination(e.target.value);
    }, []);

    const handleAmount = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setAmount(e.target.value);
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
                                            <Button fullWidth size="small" onClick={() => setUnwrapModalOpen(true)}>
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
                                            <WrapsTable unwraps={tezos.bridgeStorage?.unwraps || []} />
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
                title="Unwrap token"
                open={wrapModalOpen}
                onClose={() => {
                    setUnwrapModalOpen(false);
                    setDestination(undefined);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={unwrap}>
                            Unwrap
                        </Button>
                    </DialogActions>
                }
            >
                <TextField
                    error={!destination}
                    placeholder="Destination (0x...)"
                    value={destination || ''}
                    onChange={handleDestination}
                    fullWidth
                    margin="dense"
                />
                <TextField value={amount || 0} placeholder="Amount" onChange={handleAmount} fullWidth margin="dense" />
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
        </>
    );
};

export default Tezos;
