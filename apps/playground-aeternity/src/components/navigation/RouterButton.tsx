import React from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import { Link as RouterLink } from 'react-router-dom';

interface OwnProps extends ButtonProps {
    to: string;
}

const RouterButton: React.FC<OwnProps> = ({ to, ...props }) => (
    <Button
        {...props}
        component={React.forwardRef((linkProps, _) => (
            <RouterLink {...linkProps} to={to} />
        ))}
    />
);

export default RouterButton;
