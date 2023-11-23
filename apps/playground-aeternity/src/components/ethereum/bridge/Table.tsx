import React from 'react';
import {
    TableCell,
    TableHead as MuiTableHead,
    TableBody as MuiTableBody,
    TableRow as MuiTableRow,
    Box,
    Typography,
} from '@mui/material';

import TableRow from 'src/components/base/TableRow';
import Table from '../../base/Table';
import { BridgeMovement } from 'src/context/AppContext';

const TRow: React.FC<BridgeMovement> = ({ destination, amount, nonce }) => {
    return (
        <TableRow>
            <TableCell
                component="th"
                scope="row"
                sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: 300,
                }}
            >
                <Typography variant="caption">{destination}</Typography>
            </TableCell>
            <TableCell
                component="th"
                scope="row"
                sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: 150,
                }}
            >
                <Typography variant="caption">{amount.toString()}</Typography>
            </TableCell>
            <TableCell component="th" scope="row">
                <Typography variant="caption">{nonce.toString()}</Typography>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    movements: BridgeMovement[];
}

const TableTemplate =
    <T extends OwnProps>(Component: React.FC<T>): React.FC<T> =>
    (props) =>
        (
            <Table
                header={
                    <MuiTableHead>
                        <MuiTableRow>
                            <TableCell>Destination</TableCell>
                            <TableCell>Amount</TableCell>
                            <TableCell>Nonce</TableCell>
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const ValidatedBlocksTable: React.FC<OwnProps> = ({ movements }) => {
    if (!movements.length) {
        return (
            <MuiTableRow>
                <TableCell colSpan={6}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Typography variant="overline" textAlign="center">
                            No data
                        </Typography>
                    </Box>
                </TableCell>
            </MuiTableRow>
        );
    }

    return (
        <>
            {movements.map((movements, key) => (
                <TRow key={key} {...movements} />
            ))}
        </>
    );
};

export default TableTemplate(ValidatedBlocksTable);
