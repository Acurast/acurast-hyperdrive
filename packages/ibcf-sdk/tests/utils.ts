export interface Override {
    method: string;
    path?: string;
    responses: Record<string, any>[];
}
