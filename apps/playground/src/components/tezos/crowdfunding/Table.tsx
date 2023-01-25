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
import { TezosFundingEvent } from 'src/context/AppContext';

const TRow: React.FC<TezosFundingEvent> = ({ funder, amount }) => {
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
                <Typography variant="caption">{amount}</Typography>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    fundings: TezosFundingEvent[];
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
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const FundingTable: React.FC<OwnProps> = ({ fundings }) => {
    if (!fundings.length) {
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
            {fundings.map((funding, key) => (
                <TRow key={key} {...funding} />
            ))}
        </>
    );
};

export default TableTemplate(FundingTable);
