import React from 'react';
import { Dialog as MuiDialog, DialogContent, DialogTitle, Slide } from '@mui/material';
import type { TransitionProps } from '@mui/material/transitions';

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

interface OwnProps {
    children: React.ReactNode;
    open: boolean;
    onClose: () => void;
    title?: string;
    actions?: React.ReactElement;
}

const Dialog: React.FC<OwnProps> = (props) => {
    const { open, onClose, title, children, actions } = props;
    return (
        <MuiDialog open={open} TransitionComponent={Transition} keepMounted onClose={onClose} aria-describedby="dialog">
            {title ? <DialogTitle>{title}</DialogTitle> : null}
            <DialogContent dividers>{children}</DialogContent>
            {actions}
        </MuiDialog>
    );
};

export default Dialog;
