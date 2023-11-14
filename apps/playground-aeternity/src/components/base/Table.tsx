import * as React from 'react';
import { Table as MuiTable, TableContainer, Paper } from '@mui/material';

interface OwnProps {
    header?: React.ReactElement;
    body: React.ReactElement;
}

const Table: React.FC<OwnProps> = ({ header, body }) => {
    return (
        <TableContainer component={Paper}>
            <MuiTable aria-label="channels-table">
                {header}
                {body}
            </MuiTable>
        </TableContainer>
    );
};

export default Table;
