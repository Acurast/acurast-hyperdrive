import React from 'react';
import { Box, Container, Dialog, Grid, Typography } from '@mui/material';
import AeternityIcon from 'src/components/base/icons/aeternity';
import EthereumIcon from 'src/components/base/icons/ethereum';

import TezosBridge from 'src/components/aeternity/bridge';
import EthereumBridge from 'src/components/ethereum/bridge';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import useWalletContext from 'src/hooks/useWalletContext';
import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';
import Aeternity from 'src/services/aeternity';
import Logger from 'src/services/logger';
import EthereumSDK, { Contract } from 'src/services/ethereum';

export enum Direction {
    AeternityToSepolia = 'aeternity-sepolia',
    SepoliaToAeternity = 'sepolia-aeternity',
}

const Bridge: React.FC = () => {
    const { aeternity, network, ethereum } = useAppContext();
    const { connectAeternityWallet, address } = useWalletContext();
    const [error, setError] = React.useState('');
    const [confirming, setConfirming] = React.useState(false);
    const [operationHash, setOperationHash] = React.useState('');

    const [destination, setDestination] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();
    const [direction, updateDirection] = React.useState<Direction>(Direction.AeternityToSepolia);

    const handleDirectionChange = React.useCallback((evt: SelectChangeEvent<Direction>) => {
        updateDirection(evt.target.value as Direction);
    }, []);

    const handleDestination = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setDestination(e.target.value);
    }, []);

    const handleAmount = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setAmount(e.target.value);
    }, []);

    const bridgeToAeternity = React.useCallback(async () => {
        const bridge = new Contract(
            Constants[network].bridge_address,
            Constants[network].bridge_abi,
            EthereumSDK.getSigner(),
        );
        if (!destination || destination.length != 53 || !destination.startsWith('ak')) {
            return setError('Invalid destination!');
        }
        if (!amount || amount == '0') {
            return setError('Invalid amount!');
        }

        try {
            const result = await bridge.bridge_out(destination, amount);
            setConfirming(true);
            setOperationHash(result.hash);
            await result.wait(1);
        } catch (e: any) {
            Logger.error(e);
            setError(e);
        } finally {
            setConfirming(false);
        }
    }, [destination, amount]);

    const bridgeToEvm = React.useCallback(async () => {
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
            if (allowance === undefined) {
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

    React.useEffect(() => {
        if (direction === Direction.AeternityToSepolia) {
            setDestination(ethereum?.bridgeInfo?.account ?? '');
        } else {
            setDestination(address);
        }
    }, [address, direction, ethereum.bridgeInfo]);

    return (
        <Container sx={{ paddingY: 8 }}>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginBottom: 10 }}
            >
                <Card sx={{ minWidth: 400 }}>
                    <CardContent>
                        <Typography sx={{ fontSize: 18, marginBottom: 3 }} gutterBottom>
                            Bridge
                        </Typography>
                        <Typography sx={{ mb: 1.5 }} color="text.secondary">
                            From
                        </Typography>
                        <Grid container direction="row" spacing={1} sx={{ marginBottom: 2 }}>
                            <Grid item xs={7}>
                                <FormControl fullWidth>
                                    <InputLabel id="token-select-label">Token</InputLabel>
                                    <Select
                                        labelId="token-select-label"
                                        id="token-select"
                                        label="Token"
                                        value={direction}
                                        disabled
                                    >
                                        <MenuItem value={Direction.AeternityToSepolia}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>Æ</Box>
                                            </Box>
                                        </MenuItem>

                                        <MenuItem value={Direction.SepoliaToAeternity}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>wÆ</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>

                            <Grid item xs={5}>
                                <FormControl fullWidth>
                                    <InputLabel id="network-from-select-label">Network</InputLabel>
                                    <Select
                                        labelId="network-from-select-label"
                                        id="network-from-select"
                                        label="Network"
                                        value={direction}
                                        onChange={handleDirectionChange}
                                    >
                                        <MenuItem value={Direction.AeternityToSepolia}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon /> <Box sx={{ marginLeft: 1 }}>æternity</Box>
                                            </Box>
                                        </MenuItem>
                                        <MenuItem value={Direction.SepoliaToAeternity}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <EthereumIcon /> <Box sx={{ marginLeft: 1 }}>Ethereum</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>

                        <Typography sx={{ mb: 1.5 }} color="text.secondary">
                            To
                        </Typography>
                        <Grid container direction="row" spacing={1} sx={{ marginBottom: 3 }}>
                            <Grid item xs={7}>
                                <FormControl fullWidth>
                                    <InputLabel id="token-select-label">Token</InputLabel>
                                    <Select
                                        labelId="token-select-label"
                                        id="token-select"
                                        label="Token"
                                        value={direction}
                                        disabled
                                    >
                                        <MenuItem value={Direction.AeternityToSepolia}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>wÆ</Box>
                                            </Box>
                                        </MenuItem>

                                        <MenuItem value={Direction.SepoliaToAeternity}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>Æ</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={5}>
                                <FormControl fullWidth>
                                    <InputLabel id="network-to-select-label">Network</InputLabel>
                                    <Select
                                        labelId="network-to-select-label"
                                        id="network-to-select"
                                        label="Network"
                                        value={direction}
                                        onChange={handleDirectionChange}
                                    >
                                        <MenuItem value={Direction.AeternityToSepolia}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <EthereumIcon /> <Box sx={{ marginLeft: 1 }}>Ethereum</Box>
                                            </Box>
                                        </MenuItem>
                                        <MenuItem value={Direction.SepoliaToAeternity}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon /> <Box sx={{ marginLeft: 1 }}>æternity</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>

                        <TextField
                            fullWidth
                            id="outlined-basic"
                            label="Total Amount"
                            variant="outlined"
                            type="number"
                            sx={{ marginBottom: 2 }}
                            onChange={handleAmount}
                            value={amount || 0}
                        />

                        <TextField
                            error={!destination}
                            fullWidth
                            id="outlined-basic"
                            label="Destination Address"
                            variant="outlined"
                            type="text"
                            value={destination || ''}
                            onChange={handleDestination}
                        />
                    </CardContent>

                    <Grid container direction="row" justifyContent="center" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                {confirming ? 'Confirming...' : ''}
                            </Typography>
                        </Grid>
                    </Grid>
                    <CardActions sx={{ margin: 1, paddingTop: 6 }}>
                        {address ? (
                            direction === Direction.AeternityToSepolia ? (
                                <Button fullWidth variant="contained" onClick={bridgeToEvm}>
                                    Bridge to Sepolia
                                </Button>
                            ) : (
                                <Button fullWidth variant="contained" onClick={bridgeToAeternity}>
                                    Bridge to Aeternity
                                </Button>
                            )
                        ) : (
                            <Button fullWidth variant="contained" onClick={connectAeternityWallet}>
                                Connect Wallet
                            </Button>
                        )}
                    </CardActions>
                </Card>
            </Grid>

            <Dialog title="Error" open={!!error} onClose={() => setError('')}>
                {error}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                {direction === Direction.AeternityToSepolia ? (
                    <a
                        style={{ color: 'white' }}
                        target="_blank"
                        href={`${Constants.aeternity.explorer}/transactions/${operationHash}`}
                        rel="noreferrer"
                    >
                        AeScan
                    </a>
                ) : (
                    <a
                        style={{ color: 'white' }}
                        target="_blank"
                        href={`${Constants[network].etherscan}/tx/${operationHash}`}
                        rel="noreferrer"
                    >
                        Etherscan
                    </a>
                )}
            </Dialog>

            <Typography variant="overline">Bridging Steps</Typography>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginBottom: 10 }}
            >
                <Grid item xs={6}>
                    <TezosBridge />
                </Grid>
                <Grid item xs={6}>
                    <EthereumBridge />
                </Grid>
            </Grid>
        </Container>
    );
};
export default Bridge;
