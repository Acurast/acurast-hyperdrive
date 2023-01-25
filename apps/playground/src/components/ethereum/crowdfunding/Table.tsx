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
import { FundEvent } from 'src/context/AppContext';
import Button from 'src/components/base/Button';

interface TRowProps extends FundEvent {
    getProof: (nonce: number) => void;
}

const TRow: React.FC<TRowProps> = ({ funder, amount, nonce, getProof }) => {
    return (
        <TableRow>
            <TableCell component="th" scope="row">
                <Typography variant="caption">{funder}</Typography>
            </TableCell>
            <TableCell
                component="th"
                scope="row"
                sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: 200,
                }}
            >
                <Typography variant="caption">{amount.toString()}</Typography>
            </TableCell>
            <TableCell component="th" scope="row">
                <Button onClick={() => getProof(nonce.toNumber())}>{nonce.toString()}</Button>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    funding: FundEvent[];
    getProof: (nonce: number) => void;
}

const TableTemplate =
    <T extends OwnProps>(Component: React.FC<T>): React.FC<T> =>
    (props) =>
        (
            <Table
                header={
                    <MuiTableHead>
                        <MuiTableRow>
                            <TableCell>Funder</TableCell>
                            <TableCell>Amount</TableCell>
                            <TableCell>Nonce</TableCell>
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const FundingTable: React.FC<OwnProps> = ({ funding, getProof }) => {
    if (!funding.length) {
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
            {funding.map((fund, key) => (
                <TRow key={key} getProof={getProof} {...fund} />
            ))}
        </>
    );
};

export default TableTemplate(FundingTable);
