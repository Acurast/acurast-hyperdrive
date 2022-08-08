import React from 'react';
import { styled, TableRow as MuiTableRow } from '@mui/material';

const TableRow = styled<React.FC<{ children: React.ReactNode }>>(MuiTableRow)(({ theme }) => ({
    textDecoration: 'none',
    '&:nth-of-type(odd)': {
        backgroundColor: theme.palette.action.hover,
    },
    // hide last border
    '&:last-child td': {
        border: 0,
    },
}));

export default TableRow;
