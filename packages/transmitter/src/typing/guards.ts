import {
    OperationContentsAndResultTransaction,
    OperationContents,
    OperationContentsAndResult,
} from '@taquito/rpc/dist/types/types';
import { OpKind } from '@taquito/taquito';

export const isTransationContents = (
    op: OperationContents | OperationContentsAndResult,
): op is OperationContentsAndResultTransaction => op.kind == OpKind.TRANSACTION;
