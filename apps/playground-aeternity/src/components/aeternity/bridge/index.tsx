import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, DialogActions } from '@mui/material';
import AeternitySdk from 'src/services/aeternity';
import Button from 'src/components/base/Button';
import AeternityIcon from 'src/components/base/icons/aeternity';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Dialog from '../../base/Dialog';
import MovementsTable from './Table';
import TextField from '../../base/TextField';
import useWalletContext from 'src/hooks/useWalletContext';
import AssetCard from './AssetCard';
import Logger from 'src/services/logger';
import Aeternity from 'src/services/aeternity';

const AeternityBridge = () => {
    const { aeternity, network } = useAppContext();
    const { connectAeternityWallet, address } = useWalletContext();
    const [error, setError] = React.useState('');
    const [operationHash, setOperationHash] = React.useState('');
    const [bridgeModalOpen, setBridgeModalOpen] = React.useState(false);
    const [destination, setDestination] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();
    const [confirming, setConfirming] = React.useState(false);

    const bridge = React.useCallback(async () => {
        if (!destination || destination.length != 42 || !destination.startsWith('0x')) {
            return setError('Invalid destination!');
        }
        if (!amount || amount == '0') {
            return setError('Invalid amount!');
        }

        try {
            //const base = (await Aeternity.api.getAccountNextNonce(Aeternity.address)).nextNonce;

            const asset_contract = await Aeternity.initializeContract({
                aci: Constants.aeternity.asset_aci,
                address: aeternity.bridgeInfo?.asset.address as `ct_${string}`,
            });

            const { decodedResult: allowance } = await asset_contract.allowance({
                from_account: Aeternity.address,
                for_account: Constants.aeternity.bridge_address.replace('ct_', 'ak_'),
            });
            console.log(allowance);
            if (!allowance) {
                const create_allowance_call = await asset_contract.create_allowance(
                    Constants.aeternity.bridge_address.replace('ct_', 'ak_'),
                    amount,
                );
            } else if (allowance < BigInt(amount)) {
                const change_allowance_call = await asset_contract.change_allowance(
                    Constants.aeternity.bridge_address.replace('ct_', 'ak_'),
                    amount,
                );
            }

            const bridge_contract = await Aeternity.initializeContract({
                aci: Constants.aeternity.bridge_aci,
                address: Constants.aeternity.bridge_address,
            });
            const bridge_out_call = await bridge_contract.bridge_out([destination, amount]);

            setConfirming(true);
            setOperationHash(bridge_out_call.hash);
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
                                Aeternity
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Button fullWidth size="small" onClick={connectAeternityWallet}>
                                Connect
                            </Button>
                        </Grid>
                        <Grid item>
                            <AeternityIcon />
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    {aeternity.bridgeInfo ? <AssetCard asset={aeternity.bridgeInfo?.asset} /> : null}
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
                                            href={`${Constants.aeternity.explorer}/contracts/${Constants.aeternity.bridge_address}`}
                                            rel="noreferrer"
                                        >
                                            {Constants.aeternity.bridge_address}
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
                                            <Button fullWidth size="small" onClick={() => setBridgeModalOpen(true)}>
                                                Bridge
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
                                                Movements
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <MovementsTable movements={aeternity.bridgeInfo?.movements || []} />
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
                title="Bridge Asset"
                open={bridgeModalOpen}
                onClose={() => {
                    setBridgeModalOpen(false);
                    setDestination(undefined);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={bridge}>
                            Submit
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
                    href={`${Constants.aeternity.explorer}/transactions/${operationHash}`}
                    rel="noreferrer"
                >
                    AeScan
                </a>
            </Dialog>
        </>
    );
};

export default AeternityBridge;
