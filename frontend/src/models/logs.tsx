export interface Log {
    hash: string,
    previous_hash: string,
    timestamp: number,
    transactions?: {
        mean: number[][],
        model_bytes: string,
        size: number,
        std_dev: number[][]
    }[],
    from_address: number,
    to_address: string,
    gas_used: string,
    type: string
}